from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from app.db.commerce_models import CommerceOrder, CommerceOrderItem, CommerceOrderStatusHistory
from app.db import sync_session
from app.modules.orders.models.entity import Order, OrderItem, OrderStatus, OrderStatusHistoryEntry, PaymentMethod
from app.modules.orders.repositories.base import OrdersRepository


class SQLAlchemyOrdersRepository(OrdersRepository):
    def _order_from_row(self, db, row: CommerceOrder) -> Order:
        items = db.scalars(select(CommerceOrderItem).where(CommerceOrderItem.order_id == row.id)).all()
        history_rows = db.scalars(select(CommerceOrderStatusHistory).where(CommerceOrderStatusHistory.order_id == row.id)).all()
        order = Order(
            id=row.id,
            user_id=row.user_id,
            status=OrderStatus(row.status),
            payment_method=PaymentMethod(row.payment_method),
            payment_id=row.payment_id,
            payment_status=row.payment_status,
            total_price=row.total_price,
            items=[
                OrderItem(
                    id=item.id,
                    order_id=item.order_id,
                    sku=item.sku,
                    title=item.title,
                    qty=item.qty,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                    rule_trace=item.rule_trace,
                )
                for item in items
            ],
            status_history=[
                OrderStatusHistoryEntry(
                    from_status=OrderStatus(h.from_status) if h.from_status else None,
                    to_status=OrderStatus(h.to_status),
                    changed_at=h.changed_at,
                )
                for h in history_rows
            ],
        )
        return order

    def create_order(self, user_id: int, status: OrderStatus, payment_method: PaymentMethod) -> Order:
        with sync_session.SyncSessionLocal() as db:
            row = CommerceOrder(user_id=user_id, status=status.value, payment_method=payment_method.value, total_price=Decimal("0.00"))
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._order_from_row(db, row)

    def get_order(self, order_id: int) -> Order | None:
        with sync_session.SyncSessionLocal() as db:
            row = db.get(CommerceOrder, order_id)
            return self._order_from_row(db, row) if row else None

    def get_by_payment_id(self, payment_id: str) -> Order | None:
        with sync_session.SyncSessionLocal() as db:
            row = db.scalar(select(CommerceOrder).where(CommerceOrder.payment_id == payment_id))
            return self._order_from_row(db, row) if row else None

    def add_order_item(self, order_id: int, sku: str, title: str, qty: int, unit_price, line_total, rule_trace) -> OrderItem:
        with sync_session.SyncSessionLocal() as db:
            row = CommerceOrderItem(
                order_id=order_id,
                sku=sku,
                title=title,
                qty=qty,
                unit_price=unit_price,
                line_total=line_total,
                rule_trace=rule_trace,
            )
            db.add(row)
            order = db.get(CommerceOrder, order_id)
            order.total_price = Decimal(order.total_price) + Decimal(line_total)
            db.commit()
            db.refresh(row)
            return OrderItem(
                id=row.id,
                order_id=row.order_id,
                sku=row.sku,
                title=row.title,
                qty=row.qty,
                unit_price=row.unit_price,
                line_total=row.line_total,
                rule_trace=row.rule_trace,
            )

    def update_status(self, order_id: int, status: OrderStatus, history: OrderStatusHistoryEntry) -> Order | None:
        with sync_session.SyncSessionLocal() as db:
            row = db.get(CommerceOrder, order_id)
            if row is None:
                return None
            row.status = status.value
            db.add(
                CommerceOrderStatusHistory(
                    order_id=order_id,
                    from_status=history.from_status.value if history.from_status else None,
                    to_status=history.to_status.value,
                    changed_at=history.changed_at,
                )
            )
            db.commit()
            db.refresh(row)
            return self._order_from_row(db, row)

    def list_orders(self) -> list[Order]:
        with sync_session.SyncSessionLocal() as db:
            rows = db.scalars(select(CommerceOrder)).all()
            return [self._order_from_row(db, row) for row in rows]