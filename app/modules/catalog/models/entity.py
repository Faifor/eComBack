from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

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
    on_hand: int = 0
    reserved: int = 0
    available: int = 0


class InventoryMovementType(str, Enum):
    receipt = "receipt"
    reserve = "reserve"
    release = "release"
    sale = "sale"
    returned = "return"
    adjustment = "adjustment"


@dataclass
class InventoryMovement:
    id: int
    sku_id: int
    movement_type: InventoryMovementType
    qty: int
    reason: str | None
    source_type: str | None
    source_id: str | None
    created_at: datetime


@dataclass
class ProductAttribute:
    id: int
    product_id: int
    name: str
    value: str