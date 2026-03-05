from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str
    external_key: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    external_key: str | None = None


class CategoryRead(BaseModel):
    id: int
    name: str
    external_key: str | None = None


class ProductCreate(BaseModel):
    name: str
    category_id: int
    external_key: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    category_id: int | None = None
    external_key: str | None = None


class ProductRead(BaseModel):
    id: int
    name: str
    category_id: int
    external_key: str | None = None


class SKUCreate(BaseModel):
    product_id: int
    sku: str
    attributes: dict[str, str] = Field(default_factory=dict)


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
    sku_id: int
    stock: int


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


class ImportRowError(BaseModel):
    row: int
    message: str


class ImportReport(BaseModel):
    created: int
    updated: int
    errors: list[ImportRowError] = Field(default_factory=list)


class RevenueReport(BaseModel):
    total_revenue: float
    paid_orders: int


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