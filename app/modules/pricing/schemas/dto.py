from decimal import Decimal
from pydantic import BaseModel


class PricingRuleCreate(BaseModel):
    name: str
    priority: int = 100
    rule_type: str
    value: Decimal
    product_id: int | None = None
    variant_id: int | None = None
    min_qty: int = 1
    coupon_code: str | None = None
    active: bool = True


class PricingRuleRead(PricingRuleCreate):
    id: int


class PriceContext(BaseModel):
    user_segment: str | None = None
    channel: str | None = None


class PriceCalculateRequest(BaseModel):
    variant_id: int
    qty: int
    promo_code: str | None = None
    context: PriceContext = PriceContext()


class AppliedRuleRead(BaseModel):
    rule_id: int
    name: str
    delta: Decimal


class PriceCalculateResponse(BaseModel):
    unit_price: Decimal
    total_price: Decimal
    applied_rules: list[AppliedRuleRead]