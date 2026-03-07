from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from xml.etree import ElementTree

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.admin.schemas.dto import (
    AverageCheckReport,
    CategoryCreate,
    CategoryRead,
    ConversionReport,
    ImportReport,
    ImportRowError,
    InventoryCreate,
    InventoryRead,
    PricingRuleCreate,
    PricingRuleRead,
    ProductCreate,
    ProductRead,
    RetentionLtvReport,
    RevenueReport,
    SKUCreate,
    SKUInventoryCardRead,
    SKURead,
    TopProduct,
)
from app.modules.auth.dependencies import require_role
from app.modules.auth.models.entity import UserRole
from app.modules.catalog.schemas.dto import (
    CategoryCreate as CatalogCategoryCreate,
    InventorySet,
    ProductCreate as CatalogProductCreate,
    ProductVariantCreate,
)
from app.modules.catalog.services.service import DefaultCatalogService
from app.modules.orders.models.entity import OrderStatus
from app.modules.pricing.schemas.dto import PricingRuleCreate as PricingRuleCreateDto
from app.modules.runtime import catalog_repository, orders_repository, pricing_service

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role(UserRole.ADMIN))])
_catalog_service = DefaultCatalogService(catalog_repository)


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate) -> CategoryRead:
    item = _catalog_service.create_category(CatalogCategoryCreate(name=payload.name, parent_id=None))
    return CategoryRead(id=item.id, name=item.name, external_key=payload.external_key)


@router.get("/categories", response_model=list[CategoryRead])
def list_categories() -> list[CategoryRead]:
    return [CategoryRead(id=item.id, name=item.name, external_key=None) for item in _catalog_service.list_categories()]


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate) -> ProductRead:
    item = _catalog_service.create_product(
        CatalogProductCreate(title=payload.name, category_id=payload.category_id, base_price=Decimal("0.00"))
    )
    return ProductRead(id=item.id, name=item.title, category_id=item.category_id, external_key=payload.external_key)

@router.get("/products", response_model=list[ProductRead])
def list_products() -> list[ProductRead]:
    return [
        ProductRead(id=item.id, name=item.title, category_id=item.category_id, external_key=None)
        for item in _catalog_service.list_products()
    ]


@router.post("/skus", response_model=SKURead, status_code=status.HTTP_201_CREATED)
def create_sku(payload: SKUCreate) -> SKURead:
    item = _catalog_service.create_variant(
        ProductVariantCreate(product_id=payload.product_id, sku=payload.sku, title=payload.sku, base_price=None)
    )
    return SKURead(id=item.id, product_id=item.product_id, sku=item.sku, attributes=payload.attributes)


@router.get("/skus", response_model=list[SKURead])
def list_skus() -> list[SKURead]:
    return []


@router.post("/inventory", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
def create_inventory(payload: InventoryCreate) -> InventoryRead:
    item = _catalog_service.set_inventory(InventorySet(variant_id=payload.sku_id, qty=payload.stock))
    return InventoryRead(id=item.id, sku_id=item.variant_id, stock=item.qty)

@router.get("/skus/{sku_id}/inventory-card", response_model=SKUInventoryCardRead)
def sku_inventory_card(
    sku_id: int,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> SKUInventoryCardRead:
    inventory = _catalog_service.get_inventory(sku_id)
    if inventory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="sku inventory not found")

    movements = catalog_repository.list_inventory_movements(sku_id, created_from=created_from, created_to=created_to)
    return SKUInventoryCardRead(
        sku_id=sku_id,
        on_hand=inventory.on_hand,
        reserved=inventory.reserved,
        available=inventory.available,
        movements=[
            {
                "id": m.id,
                "sku_id": m.sku_id,
                "movement_type": m.movement_type.value,
                "qty": m.qty,
                "reason": m.reason,
                "source_type": m.source_type,
                "source_id": m.source_id,
                "created_at": m.created_at,
            }
            for m in movements
        ],
    )


@router.post("/pricing-rules", response_model=PricingRuleRead, status_code=status.HTTP_201_CREATED)
def create_pricing_rule(payload: PricingRuleCreate) -> PricingRuleRead:
    created = pricing_service.create_rule(
        PricingRuleCreateDto(
            name=payload.name,
            priority=100,
            rule_type="percent",
            value=Decimal(str(payload.discount_percent)),
            product_id=None,
            variant_id=None,
            min_qty=1,
            coupon_code=None,
            active=payload.is_active,
        )
    )
    return PricingRuleRead(id=created.id, name=created.name, discount_percent=float(created.value), is_active=created.active)


@router.get("/pricing-rules", response_model=list[PricingRuleRead])
def list_pricing_rules() -> list[PricingRuleRead]:
    rules = pricing_service.list_rules()
    return [PricingRuleRead(id=i.id, name=i.name, discount_percent=float(i.value), is_active=i.active) for i in rules]


def _read_xlsx(content: bytes) -> list[dict[str, str]]:
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            for text_node in root.findall(".//{*}t"):
                shared_strings.append(text_node.text or "")

        sheet_root = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows: list[list[str]] = []
        for row in sheet_root.findall(".//{*}row"):
            values: list[str] = []
            for cell in row.findall("{*}c"):
                cell_type = cell.attrib.get("t")
                value_node = cell.find("{*}v")
                raw_value = "" if value_node is None or value_node.text is None else value_node.text
                values.append(shared_strings[int(raw_value)] if cell_type == "s" and raw_value else raw_value)
            rows.append(values)

    if not rows:
        return []
    headers = rows[0]
    return [{header: row[idx] if idx < len(row) else "" for idx, header in enumerate(headers)} for row in rows[1:]]

def _load_import_rows(filename: str, content: bytes) -> list[dict[str, str]]:
    if filename.endswith(".csv"):
        return [dict(item) for item in csv.DictReader(io.StringIO(content.decode("utf-8-sig")))]
    if filename.endswith(".xlsx"):
        return _read_xlsx(content)
    raise HTTPException(status_code=400, detail="Only CSV/XLSX files are supported")

@router.post("/imports/products", response_model=ImportReport)
async def import_products(filename: str, content: str, dry_run: bool = True) -> ImportReport:
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    rows = _load_import_rows(filename.lower(), content.encode("utf-8"))

    report = ImportReport(created=0, updated=0, errors=[])

    for idx, row in enumerate(rows, start=2):
        try:
            sku_code = row["sku"].strip()
            product_name = row["product_name"].strip()
            category_name = row["category_name"].strip()
            stock = int(float(row["stock"]))

            if dry_run:
                report.created += 1
                continue

            category = next((c for c in _catalog_service.list_categories() if c.name == category_name), None)
            if category is None:
                category = _catalog_service.create_category(CatalogCategoryCreate(name=category_name, parent_id=None))

            product = _catalog_service.create_product(
                CatalogProductCreate(title=product_name, category_id=category.id, base_price=Decimal("0.00"))
            )
            variant = _catalog_service.create_variant(
                ProductVariantCreate(product_id=product.id, sku=sku_code, title=sku_code, base_price=None)
            )
            _catalog_service.set_inventory(InventorySet(variant_id=variant.id, qty=stock))
            report.created += 1
        except Exception as exc:  # noqa: BLE001
            report.errors.append(ImportRowError(row=idx, message=str(exc)))

    return report


@router.get("/reports/revenue", response_model=RevenueReport)
def revenue_report() -> RevenueReport:
    paid = [o for o in orders_repository.list_orders() if o.status in {OrderStatus.paid, OrderStatus.completed}]
    total = sum(float(o.total_price) for o in paid)
    return RevenueReport(total_revenue=total, paid_orders=len(paid))


@router.get("/reports/top-products", response_model=list[TopProduct])
def top_products_report(limit: int = 5) -> list[TopProduct]:
    counts: dict[str, int] = defaultdict(int)
    for order in orders_repository.list_orders():
        for item in order.items:
            counts[item.title] += item.qty
    ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]
    return [TopProduct(product_id=idx + 1, product_name=name, units_sold=units) for idx, (name, units) in enumerate(ranked)]


@router.get("/reports/conversion", response_model=ConversionReport)
def conversion_report() -> ConversionReport:
    orders = orders_repository.list_orders()
    users = {order.user_id for order in orders}
    conversion_rate = len(orders) / len(users) if users else 0
    return ConversionReport(total_orders=len(orders), total_users=len(users), conversion_rate=conversion_rate)


@router.get("/reports/average-check", response_model=AverageCheckReport)
def average_check_report() -> AverageCheckReport:
    orders = orders_repository.list_orders()
    if not orders:
        return AverageCheckReport(average_check=0)
    total = sum(float(order.total_price) for order in orders)
    return AverageCheckReport(average_check=total / len(orders))


@router.get("/reports/retention-ltv", response_model=RetentionLtvReport)
def retention_ltv_report() -> RetentionLtvReport:
    orders = orders_repository.list_orders()
    by_user: dict[int, int] = defaultdict(int)
    spend: dict[int, float] = defaultdict(float)
    for order in orders:
        by_user[order.user_id] += 1
        spend[order.user_id] += float(order.total_price)

    total_users = len(by_user)
    returning_users = sum(1 for count in by_user.values() if count > 1)
    return RetentionLtvReport(
        returning_users=returning_users,
        retention_rate=(returning_users / total_users) if total_users else 0,
        average_ltv=(sum(spend.values()) / total_users) if total_users else 0,
    )