from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class CartItem:
    id: int
    cart_id: int
    variant_id: int
    sku: str
    title: str
    qty: int
    unit_price: Decimal
    total_price: Decimal
    rule_trace: list[dict] = field(default_factory=list)


@dataclass
class Cart:
    id: int
    user_id: int
    currency: str = "USD"
    items: list[CartItem] = field(default_factory=list)