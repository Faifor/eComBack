from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import zipfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from xml.etree import ElementTree

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select

from app.db import sync_session
from app.db.commerce_models import (
    CommerceCategory,
    CommerceImportLedger,
    CommerceInventory,
    CommerceProduct,
    CommerceVariant,
)
from app.modules.admin.reports import SQLAdminReports
from app.modules.admin.schemas.dto import (
    AverageCheckReport,
    BulkOperationReport,
    BulkPriceUpdateItem,
    BulkStatusUpdateItem,
    BulkStockUpdateItem,
    CategoryCreate,
    CategoryRead,
    ConversionReport,
    ImportIdempotencyInfo,
    ImportProductsRequest,
    ImportReport,
    ImportRowError,
    InventoryCreate,
    InventoryRead,
    MetricsBusinessRules,
    PricingRuleCreate,
    PricingRuleRead,
    ProductCreate,
    ProductDescriptionUpdate,
    ProductRead,
    ReportFilters,
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
    ProductImageRead,
    ProductCreate as CatalogProductCreate,
    ProductVariantCreate,
)
from app.modules.catalog.services.service import DefaultCatalogService
from app.modules.pricing.schemas.dto import PricingRuleCreate as PricingRuleCreateDto
from app.modules.runtime import catalog_repository, pricing_service

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role(UserRole.ADMIN))])
_catalog_service = DefaultCatalogService(catalog_repository)
_reports = SQLAdminReports()
_media_root = Path(os.getenv("MEDIA_ROOT", "media"))


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
        CatalogProductCreate(title=payload.name, category_id=payload.category_id, base_price=Decimal("0.00"), description=payload.description)
    )
    return ProductRead(id=item.id, name=item.title, category_id=item.category_id, external_key=payload.external_key, description=item.description)

@router.get("/products", response_model=list[ProductRead])
def list_products() -> list[ProductRead]:
    return [
        ProductRead(id=item.id, name=item.title, category_id=item.category_id, external_key=None, description=item.description)
        for item in _catalog_service.list_products()
    ]




@router.put("/products/{product_id}/description", response_model=ProductRead)
def update_product_description(product_id: int, payload: ProductDescriptionUpdate) -> ProductRead:
    with sync_session.SyncSessionLocal() as db:
        product = db.get(CommerceProduct, product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")
        product.description = payload.description
        db.commit()
        db.refresh(product)
        return ProductRead(id=product.id, name=product.title, category_id=product.category_id, external_key=None, description=product.description)


@router.post("/products/{product_id}/images", response_model=list[ProductImageRead], status_code=status.HTTP_201_CREATED)
def upload_product_images(product_id: int, files: list[UploadFile] = File(...)) -> list[ProductImageRead]:
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no files provided")
    uploaded: list[ProductImageRead] = []
    product_dir = _media_root / "products" / str(product_id)
    product_dir.mkdir(parents=True, exist_ok=True)
    existing_count = len(catalog_repository.list_product_images(product_id))
    for index, upload in enumerate(files):
        extension = Path(upload.filename or "image").suffix or ".bin"
        file_name = f"{uuid4().hex}{extension}"
        target = product_dir / file_name
        with target.open("wb") as destination:
            destination.write(upload.file.read())
        try:
            image = _catalog_service.add_product_image(
                product_id,
                image_url=str(target),
                is_primary=existing_count == 0 and index == 0,
                sort_order=existing_count + index,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        uploaded.append(image)
    return uploaded


@router.post("/skus", response_model=SKURead, status_code=status.HTTP_201_CREATED)
def create_sku(payload: SKUCreate) -> SKURead:
    item = _catalog_service.create_variant(
        ProductVariantCreate(product_id=payload.product_id, sku=payload.sku, title=payload.sku, base_price=None)
    )
    return SKURead(id=item.id, product_id=item.product_id, sku=item.sku, attributes=payload.attributes or {})


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

@router.post("/bulk/sku-prices", response_model=BulkOperationReport)
def bulk_update_sku_prices(items: list[BulkPriceUpdateItem]) -> BulkOperationReport:
    report = BulkOperationReport(updated=0, errors=[])
    with sync_session.SyncSessionLocal() as db:
        for idx, item in enumerate(items, start=1):
            variant = db.scalar(select(CommerceVariant).where(CommerceVariant.sku == item.sku))
            if variant is None:
                report.errors.append(ImportRowError(row=idx, field="sku", reason="SKU not found"))
                continue
            variant.base_price = Decimal(str(item.price))
            report.updated += 1
        db.commit()
    return report


@router.post("/bulk/sku-stocks", response_model=BulkOperationReport)
def bulk_update_sku_stocks(items: list[BulkStockUpdateItem]) -> BulkOperationReport:
    report = BulkOperationReport(updated=0, errors=[])
    for idx, item in enumerate(items, start=1):
        variant = catalog_repository.get_variant_by_sku(item.sku)
        if variant is None:
            report.errors.append(ImportRowError(row=idx, field="sku", reason="SKU not found"))
            continue
        _catalog_service.set_inventory(InventorySet(variant_id=variant.id, qty=item.stock))
        report.updated += 1
    return report


@router.post("/bulk/sku-statuses", response_model=BulkOperationReport)
def bulk_update_sku_statuses(items: list[BulkStatusUpdateItem]) -> BulkOperationReport:
    report = BulkOperationReport(updated=0, errors=[])
    with sync_session.SyncSessionLocal() as db:
        for idx, item in enumerate(items, start=1):
            variant = db.scalar(select(CommerceVariant).where(CommerceVariant.sku == item.sku))
            if variant is None:
                report.errors.append(ImportRowError(row=idx, field="sku", reason="SKU not found"))
                continue
            variant.status = item.status
            report.updated += 1
        db.commit()
    return report


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
async def import_products(
    payload: ImportProductsRequest,
    dry_run: bool = True,
    upsert: bool = False,
    rollback_on_error: bool = False,
    external_key: str = "products-import",
    version: str | None = None,
) -> ImportReport:
    filename = payload.filename
    content = payload.content
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    

    rows = _load_import_rows(filename.lower(), content.encode("utf-8"))
    report = ImportReport(created=0, updated=0, skipped=0, idempotency=[], errors=[])

    with sync_session.SyncSessionLocal() as db:
        for idx, row in enumerate(rows, start=2):
            try:
                sku_code = row["sku"].strip()
                product_name = row["product_name"].strip()
                category_name = row["category_name"].strip()
                stock = int(float(row["stock"]))
                row_external_key = (row.get("external_key") or external_key or sku_code).strip()
                row_version = (row.get("version") or version or "1").strip()
                content_hash = hashlib.sha256(
                    json.dumps(row, sort_keys=True, ensure_ascii=False).encode("utf-8")
                ).hexdigest()

                existing_ledger = db.scalar(
                    select(CommerceImportLedger).where(
                        CommerceImportLedger.external_key == row_external_key,
                        CommerceImportLedger.version == row_version,
                        CommerceImportLedger.content_hash == content_hash,
                    )
                )
                if existing_ledger is not None:
                    report.skipped += 1
                    report.idempotency.append(
                        ImportIdempotencyInfo(
                            external_key=row_external_key,
                            version=row_version,
                            content_hash=content_hash,
                            action="skipped",
                        )
                    )
                    continue

                existing_variant = db.scalar(select(CommerceVariant).where(CommerceVariant.sku == sku_code))
                action = "created"
                if existing_variant is not None and not upsert:
                    raise ValueError("SKU already exists and upsert=false")

                if not dry_run:
                    category = db.scalar(select(CommerceCategory).where(CommerceCategory.name == category_name))
                    if category is None:
                        category = CommerceCategory(name=category_name, parent_id=None)
                        db.add(category)
                        db.flush()

                    if existing_variant is None:
                        product = CommerceProduct(title=product_name, category_id=category.id, base_price=Decimal("0.00"))
                        db.add(product)
                        db.flush()
                        variant = CommerceVariant(
                            product_id=product.id,
                            sku=sku_code,
                            title=sku_code,
                            base_price=Decimal("0.00"),
                            status="active",
                        )
                        db.add(variant)
                        db.flush()
                        inventory = CommerceInventory(variant_id=variant.id, qty=stock)
                        db.add(inventory)
                        report.created += 1
                    else:
                        action = "updated"
                        product = db.get(CommerceProduct, existing_variant.product_id)
                        if product is not None:
                            product.title = product_name
                            product.category_id = category.id
                        inventory = db.scalar(select(CommerceInventory).where(CommerceInventory.variant_id == existing_variant.id))
                        if inventory is None:
                            db.add(CommerceInventory(variant_id=existing_variant.id, qty=stock))
                        else:
                            inventory.qty = stock
                        report.updated += 1

                    db.add(
                        CommerceImportLedger(
                            external_key=row_external_key,
                            version=row_version,
                            content_hash=content_hash,
                            sku=sku_code,
                        )
                    )
                else:
                    if existing_variant is None:
                        report.created += 1
                    else:
                        action = "updated"
                        report.updated += 1

                report.idempotency.append(
                    ImportIdempotencyInfo(
                        external_key=row_external_key,
                        version=row_version,
                        content_hash=content_hash,
                        action=action,
                    )
                )
            except KeyError as exc:
                report.errors.append(ImportRowError(row=idx, field=str(exc).strip("'"), reason="Required field is missing"))
            except Exception as exc:  # noqa: BLE001
                report.errors.append(ImportRowError(row=idx, field="row", reason=str(exc)))

        if dry_run:
            db.rollback()
        elif report.errors and rollback_on_error:
            db.rollback()
            report.created = 0
            report.updated = 0
            report.skipped = 0
            report.idempotency = [item for item in report.idempotency if item.action == "skipped"]
        else:
            db.commit()

    return report

@router.get("/reports/business-rules", response_model=MetricsBusinessRules)
def metrics_business_rules() -> MetricsBusinessRules:
    return MetricsBusinessRules(**_reports.business_rules())



@router.get("/reports/revenue", response_model=RevenueReport)
def revenue_report(
    from_dt: datetime | None = None,
    to_dt: datetime | None = None,
    group_by: str = "day",
    category_id: int | None = None,
    channel: str | None = None,
    promo_code: str | None = None,
) -> RevenueReport:
    filters = ReportFilters.model_validate(
        {
            "from": from_dt,
            "to": to_dt,
            "group_by": group_by,
            "category_id": category_id,
            "channel": channel,
            "promo_code": promo_code,
        }
    )
    return RevenueReport(**_reports.revenue(filters=filters, group_by=filters.group_by))


@router.get("/reports/top-products", response_model=list[TopProduct])
def top_products_report(
    limit: int = 5,
    from_dt: datetime | None = None,
    to_dt: datetime | None = None,
    category_id: int | None = None,
    channel: str | None = None,
    promo_code: str | None = None,
) -> list[TopProduct]:
    filters = ReportFilters.model_validate(
        {
            "from": from_dt,
            "to": to_dt,
            "category_id": category_id,
            "channel": channel,
            "promo_code": promo_code,
        }
    )
    return [TopProduct(**item) for item in _reports.top_products(filters=filters, limit=limit)]


@router.get("/reports/conversion", response_model=ConversionReport)
def conversion_report(
    from_dt: datetime | None = None,
    to_dt: datetime | None = None,
    category_id: int | None = None,
    channel: str | None = None,
    promo_code: str | None = None,
) -> ConversionReport:
    filters = ReportFilters.model_validate(
        {
            "from": from_dt,
            "to": to_dt,
            "category_id": category_id,
            "channel": channel,
            "promo_code": promo_code,
        }
    )
    return ConversionReport(**_reports.conversion(filters=filters))


@router.get("/reports/average-check", response_model=AverageCheckReport)
def average_check_report(
    from_dt: datetime | None = None,
    to_dt: datetime | None = None,
    category_id: int | None = None,
    channel: str | None = None,
    promo_code: str | None = None,
) -> AverageCheckReport:
    filters = ReportFilters.model_validate(
        {
            "from": from_dt,
            "to": to_dt,
            "category_id": category_id,
            "channel": channel,
            "promo_code": promo_code,
        }
    )
    return AverageCheckReport(**_reports.average_check(filters=filters))


@router.get("/reports/retention-ltv", response_model=RetentionLtvReport)
def retention_ltv_report(
    from_dt: datetime | None = None,
    to_dt: datetime | None = None,
    category_id: int | None = None,
    channel: str | None = None,
    promo_code: str | None = None,
) -> RetentionLtvReport:
    filters = ReportFilters.model_validate(
        {
            "from": from_dt,
            "to": to_dt,
            "category_id": category_id,
            "channel": channel,
            "promo_code": promo_code,
        }
    )
    return RetentionLtvReport(**_reports.retention_ltv(filters=filters))
