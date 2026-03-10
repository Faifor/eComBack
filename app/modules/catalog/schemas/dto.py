from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str
    parent_id: int | None = None


class CategoryRead(BaseModel):
    id: int
    name: str
    parent_id: int | None = None


class ProductImageRead(BaseModel):
    id: int
    product_id: int
    image_url: str
    is_primary: bool = False
    sort_order: int = 0


class ProductCreate(BaseModel):
    title: str
    category_id: int
    base_price: Decimal
    description: str | None = None


class ProductRead(BaseModel):
    id: int
    title: str
    category_id: int
    base_price: Decimal
    description: str | None = None
    images: list[ProductImageRead] = Field(default_factory=list)
    average_rating: float = 0.0
    reviews_count: int = 0


class ProductVariantCreate(BaseModel):
    product_id: int
    sku: str
    title: str
    base_price: Decimal | None = None


class ProductVariantRead(BaseModel):
    id: int
    product_id: int
    sku: str
    title: str
    base_price: Decimal | None = None
    attributes: list["ProductAttributeRead"] = Field(default_factory=list)


class InventorySet(BaseModel):
    variant_id: int
    qty: int


class InventoryRead(BaseModel):
    id: int
    variant_id: int
    qty: int
    on_hand: int = 0
    reserved: int = 0
    available: int = 0


class ProductAttributeCreate(BaseModel):
    product_id: int
    variant_id: int | None = None
    name: str
    value: str


class ProductAttributeRead(BaseModel):
    id: int
    product_id: int
    variant_id: int | None = None
    name: str
    value: str


class ProductVariantDetailsRead(ProductVariantRead):
    attributes: list[ProductAttributeRead] = Field(default_factory=list)
    inventory: InventoryRead | None = None


class ProductReviewCreate(BaseModel):
    user_id: int
    rating: int = Field(ge=1, le=5)
    review: str


class ProductReviewRead(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    review: str
    created_at: datetime


class ProductDetailsRead(ProductRead):
    attributes: list[ProductAttributeRead] = Field(default_factory=list)
    variants: list[ProductVariantRead] = Field(default_factory=list)
    reviews: list[ProductReviewRead] = Field(default_factory=list)
