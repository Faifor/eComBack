from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, Literal


class CategoryCreate(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    external_key: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    external_key: str | None = None


class CategoryRead(BaseModel):
    id: int
    name: str
    external_key: str | None = None


class ProductCreate(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    category_id: int = Field(gt=0)
    external_key: str | None = None
    description: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    category_id: int | None = None
    external_key: str | None = None


class ProductRead(BaseModel):
    id: int
    name: str
    category_id: int
    external_key: str | None = None
    description: str | None = None


class ProductDescriptionUpdate(BaseModel):
    description: str


class SKUCreate(BaseModel):
    product_id: int = Field(gt=0)
    sku: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    attributes: dict[str, str] | None = None


class SKUUpdate(BaseModel):
    product_id: int | None = None
    sku: str | None = None
    attributes: dict[str, str] | None = None


class SKURead(BaseModel):
    id: int
    product_id: int
    sku: str
    attributes: dict[str, str] = Field(default_factory=dict)


class InventoryCreate(BaseModel):
    sku_id: int = Field(gt=0)
    stock: int = Field(ge=0)


class InventoryUpdate(BaseModel):
    sku_id: int | None = None
    stock: int | None = None


class InventoryRead(BaseModel):
    id: int
    sku_id: int
    stock: int


class PricingRuleCreate(BaseModel):
    name: str
    discount_percent: float = Field(ge=0, le=100)
    is_active: bool = True


class PricingRuleUpdate(BaseModel):
    name: str | None = None
    discount_percent: float | None = Field(default=None, ge=0, le=100)
    is_active: bool | None = None


class PricingRuleRead(BaseModel):
    id: int
    name: str
    discount_percent: float
    is_active: bool


class OrderCreate(BaseModel):
    user_id: int
    sku_id: int
    quantity: int = Field(ge=1)
    unit_price: float = Field(gt=0)
    status: str = 'created'


class OrderUpdate(BaseModel):
    user_id: int | None = None
    sku_id: int | None = None
    quantity: int | None = Field(default=None, ge=1)
    unit_price: float | None = Field(default=None, gt=0)
    status: str | None = None


class OrderRead(BaseModel):
    id: int
    user_id: int
    sku_id: int
    quantity: int
    unit_price: float
    status: str
    created_at: datetime


class AdminUserCreate(BaseModel):
    email: str
    role: str = 'admin'


class AdminUserUpdate(BaseModel):
    email: str | None = None
    role: str | None = None


class AdminUserRead(BaseModel):
    id: int
    email: str
    role: str

class ImportProductsRequest(BaseModel):
    filename: str
    content: str

class ImportRowError(BaseModel):
    row: int
    field: str
    reason: str


class ImportIdempotencyInfo(BaseModel):
    external_key: str
    version: str
    content_hash: str
    action: Literal["created", "updated", "skipped"]


class ImportReport(BaseModel):
    created: int
    updated: int
    skipped: int = 0
    idempotency: list[ImportIdempotencyInfo] = Field(default_factory=list)
    errors: list[ImportRowError] = Field(default_factory=list)


class BulkPriceUpdateItem(BaseModel):
    sku: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    price: float = Field(gt=0)


class BulkStockUpdateItem(BaseModel):
    sku: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    stock: int = Field(ge=0)


class BulkStatusUpdateItem(BaseModel):
    sku: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    status: Literal["active", "inactive", "archived"]


class BulkOperationReport(BaseModel):
    updated: int
    errors: list[ImportRowError] = Field(default_factory=list)

class ReportFilters(BaseModel):
    from_dt: datetime | None = Field(default=None, alias="from")
    to_dt: datetime | None = Field(default=None, alias="to")
    group_by: Literal["day", "week", "month"] = "day"
    category_id: int | None = None
    channel: str | None = None
    promo_code: str | None = None


class RevenueSeriesPoint(BaseModel):
    bucket: str
    revenue: float
    orders: int

class RevenueReport(BaseModel):
    total_revenue: float
    paid_orders: int
    group_by: str
    series: list[RevenueSeriesPoint] = Field(default_factory=list)


class TopProduct(BaseModel):
    product_id: int
    product_name: str
    units_sold: int


class ConversionReport(BaseModel):
    total_orders: int
    total_users: int
    conversion_rate: float


class AverageCheckReport(BaseModel):
    average_check: float


class RetentionLtvReport(BaseModel):
    returning_users: int
    retention_rate: float
    average_ltv: float

class MetricsBusinessRules(BaseModel):
    paid_statuses: list[str]
    paid_payment_statuses: list[str]
    revenue_formula: str
    retention_formula: str
    average_check_formula: str

class InventoryMovementRead(BaseModel):
    id: int
    sku_id: int
    movement_type: str
    qty: int
    reason: str | None = None
    source_type: str | None = None
    source_id: str | None = None
    created_at: datetime


class SKUInventoryCardRead(BaseModel):
    sku_id: int
    on_hand: int
    reserved: int
    available: int
    movements: list[InventoryMovementRead] = Field(default_factory=list)