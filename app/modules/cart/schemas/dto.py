from decimal import Decimal
from pydantic import BaseModel


class CartCreate(BaseModel):
    user_id: int

class CartItemUpsert(BaseModel):
    variant_id: int
    qty: int
    promo_code: str | None = None


class CartItemRead(BaseModel):
    id: int
    cart_id: int
    variant_id: int
    sku: str
    title: str
    qty: int
    unit_price: Decimal
    total_price: Decimal
    rule_trace: list[dict]


class CartRead(BaseModel):
    id: int
    user_id: int
    currency: str
    items: list[CartItemRead]