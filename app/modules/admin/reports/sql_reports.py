from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Select, and_, distinct, exists, func, select

from app.db import sync_session
from app.db.commerce_models import CommerceOrder, CommerceOrderItem, CommerceProduct, CommerceVariant
from app.modules.auth.models.entity import User

PAID_ORDER_STATUSES = {"paid", "completed"}
PAID_PAYMENT_STATUSES = {"paid", "succeeded"}


@dataclass(frozen=True)
class ReportFilters:
    from_dt: datetime | None = None
    to_dt: datetime | None = None
    category_id: int | None = None
    channel: str | None = None
    promo_code: str | None = None


class SQLAdminReports:
    """SQL агрегаты для admin/reports.

    Бизнес-правила:
    1. Заказ считается монетизированным, если status in {paid, completed}
       ИЛИ payment_status in {paid, succeeded}.
    2. Выручка считается по сумме line_total в order_items по монетизированным заказам.
    3. Average check = revenue / count(distinct монетизированных заказов).
    4. Retention: доля пользователей с >=2 монетизированными заказами среди
       пользователей с >=1 монетизированным заказом в периоде.
    """

    def _paid_orders_query(self, filters: ReportFilters) -> Select:
        conditions = [
            (CommerceOrder.status.in_(PAID_ORDER_STATUSES)) | (CommerceOrder.payment_status.in_(PAID_PAYMENT_STATUSES))
        ]

        if filters.from_dt is not None:
            conditions.append(CommerceOrder.created_at >= filters.from_dt)
        if filters.to_dt is not None:
            conditions.append(CommerceOrder.created_at <= filters.to_dt)
        if filters.channel:
            conditions.append(CommerceOrder.sales_channel == filters.channel)
        if filters.promo_code:
            conditions.append(CommerceOrder.promo_code == filters.promo_code)
        if filters.category_id is not None:
            conditions.append(
                exists(
                    select(1)
                    .select_from(CommerceOrderItem)
                    .join(CommerceVariant, CommerceVariant.sku == CommerceOrderItem.sku)
                    .join(CommerceProduct, CommerceProduct.id == CommerceVariant.product_id)
                    .where(
                        CommerceOrderItem.order_id == CommerceOrder.id,
                        CommerceProduct.category_id == filters.category_id,
                    )
                )
            )

        return select(CommerceOrder.id, CommerceOrder.user_id, CommerceOrder.created_at).where(and_(*conditions))

    def revenue(self, filters: ReportFilters, group_by: str = "day") -> dict:
        paid_orders_sq = self._paid_orders_query(filters).subquery()
        bucket_expr = self._bucket_expr(group_by, paid_orders_sq.c.created_at)

        with sync_session.SyncSessionLocal() as db:
            total_revenue = db.scalar(
                select(func.coalesce(func.sum(CommerceOrderItem.line_total), 0))
                .join(paid_orders_sq, paid_orders_sq.c.id == CommerceOrderItem.order_id)
            )
            paid_orders = db.scalar(select(func.count()).select_from(paid_orders_sq)) or 0

            grouped = db.execute(
                select(
                    bucket_expr.label("bucket"),
                    func.coalesce(func.sum(CommerceOrderItem.line_total), 0).label("revenue"),
                    func.count(distinct(CommerceOrderItem.order_id)).label("orders"),
                )
                .select_from(CommerceOrderItem)
                .join(paid_orders_sq, paid_orders_sq.c.id == CommerceOrderItem.order_id)
                .group_by(bucket_expr)
                .order_by(bucket_expr)
            ).all()

        return {
            "total_revenue": float(total_revenue),
            "paid_orders": paid_orders,
            "group_by": group_by,
            "series": [
                {
                    "bucket": str(row.bucket),
                    "revenue": float(row.revenue),
                    "orders": int(row.orders),
                }
                for row in grouped
            ],
        }

    def top_products(self, filters: ReportFilters, limit: int = 5) -> list[dict]:
        paid_orders_sq = self._paid_orders_query(filters).subquery()
        with sync_session.SyncSessionLocal() as db:
            rows = db.execute(
                select(
                    CommerceOrderItem.title,
                    func.sum(CommerceOrderItem.qty).label("units"),
                )
                .join(paid_orders_sq, paid_orders_sq.c.id == CommerceOrderItem.order_id)
                .group_by(CommerceOrderItem.title)
                .order_by(func.sum(CommerceOrderItem.qty).desc())
                .limit(limit)
            ).all()
        return [
            {"product_id": idx + 1, "product_name": row.title, "units_sold": int(row.units)} for idx, row in enumerate(rows)
        ]

    def conversion(self, filters: ReportFilters) -> dict:
        paid_orders_sq = self._paid_orders_query(filters).subquery()
        with sync_session.SyncSessionLocal() as db:
            total_orders = db.scalar(select(func.count()).select_from(paid_orders_sq)) or 0

            user_conditions = []
            if filters.from_dt is not None:
                user_conditions.append(User.created_at >= filters.from_dt)
            if filters.to_dt is not None:
                user_conditions.append(User.created_at <= filters.to_dt)

            total_users = db.scalar(select(func.count(User.id)).where(and_(*user_conditions))) if user_conditions else db.scalar(select(func.count(User.id)))
            total_users = total_users or 0

        return {
            "total_orders": total_orders,
            "total_users": total_users,
            "conversion_rate": (total_orders / total_users) if total_users else 0,
        }

    def average_check(self, filters: ReportFilters) -> dict:
        paid_orders_sq = self._paid_orders_query(filters).subquery()
        with sync_session.SyncSessionLocal() as db:
            totals = db.execute(
                select(
                    func.coalesce(func.sum(CommerceOrderItem.line_total), 0).label("revenue"),
                    func.count(distinct(CommerceOrderItem.order_id)).label("orders"),
                ).join(paid_orders_sq, paid_orders_sq.c.id == CommerceOrderItem.order_id)
            ).one()

        orders_count = int(totals.orders or 0)
        revenue = float(totals.revenue or 0)
        return {"average_check": (revenue / orders_count) if orders_count else 0}

    def retention_ltv(self, filters: ReportFilters) -> dict:
        paid_orders_sq = self._paid_orders_query(filters).subquery()
        with sync_session.SyncSessionLocal() as db:
            user_orders = db.execute(
                select(
                    paid_orders_sq.c.user_id,
                    func.count(distinct(paid_orders_sq.c.id)).label("orders_count"),
                    func.coalesce(func.sum(CommerceOrderItem.line_total), 0).label("ltv"),
                )
                .select_from(paid_orders_sq)
                .join(CommerceOrderItem, CommerceOrderItem.order_id == paid_orders_sq.c.id)
                .group_by(paid_orders_sq.c.user_id)
            ).all()

        total_users = len(user_orders)
        returning_users = sum(1 for row in user_orders if int(row.orders_count) > 1)
        average_ltv = (sum(float(row.ltv) for row in user_orders) / total_users) if total_users else 0

        return {
            "returning_users": returning_users,
            "retention_rate": (returning_users / total_users) if total_users else 0,
            "average_ltv": average_ltv,
        }

    @staticmethod
    def _bucket_expr(group_by: str, created_at_col):
        if group_by == "month":
            return func.strftime("%Y-%m-01", created_at_col)
        if group_by == "week":
            return func.strftime("%Y-%W-1", created_at_col)
        return func.strftime("%Y-%m-%d", created_at_col)

    @staticmethod
    def business_rules() -> dict[str, object]:
        return {
            "paid_statuses": sorted(PAID_ORDER_STATUSES),
            "paid_payment_statuses": sorted(PAID_PAYMENT_STATUSES),
            "revenue_formula": "sum(order_items.line_total) for paid/completed orders",
            "retention_formula": "users_with_2_plus_paid_orders / users_with_1_plus_paid_orders",
            "average_check_formula": "revenue / paid_orders",
        }