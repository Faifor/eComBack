from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Category:
    id: int
    name: str
    parent_id: int | None = None


@dataclass
class Product:
    id: int
    title: str
    category_id: int
    base_price: Decimal
    is_active: bool = True


@dataclass
class ProductVariant:
    id: int
    product_id: int
    sku: str
    title: str
    base_price: Decimal | None = None


@dataclass
class Inventory:
    id: int
    variant_id: int
    qty: int


@dataclass
class ProductAttribute:
    id: int
    product_id: int
    name: str
    value: str