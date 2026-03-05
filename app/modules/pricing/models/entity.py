from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class PricingRule:
    id: int
    name: str
    priority: int
    rule_type: str  # percent|fixed
    value: Decimal
    product_id: int | None = None
    variant_id: int | None = None
    min_qty: int = 1
    coupon_code: str | None = None
    active: bool = True


@dataclass
class AppliedRule:
    rule_id: int
    name: str
    delta: Decimal


@dataclass
class PriceCalculation:
    unit_price: Decimal
    total_price: Decimal
    applied_rules: list[AppliedRule] = field(default_factory=list)