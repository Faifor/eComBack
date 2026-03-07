from decimal import Decimal
from pydantic import BaseModel



class CategoryCreate(BaseModel):
    name: str
    parent_id: int | None = None


class CategoryRead(BaseModel):
    id: int
    name: str
    parent_id: int | None = None


class ProductCreate(BaseModel):
    title: str
    category_id: int
    base_price: Decimal


class ProductRead(BaseModel):
    id: int
    title: str
    category_id: int
    base_price: Decimal

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
    name: str
    value: str


class ProductAttributeRead(BaseModel):
    id: int
    product_id: int
    name: str
    value: str