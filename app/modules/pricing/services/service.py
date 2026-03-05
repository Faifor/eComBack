from decimal import Decimal

from app.modules.catalog.repositories.base import CatalogRepository
from app.modules.pricing.models.entity import AppliedRule, PriceCalculation, PricingRule
from app.modules.pricing.repositories.base import PricingRepository
from app.modules.pricing.schemas.dto import (
    AppliedRuleRead,
    PriceCalculateRequest,
    PriceCalculateResponse,
    PricingRuleCreate,
    PricingRuleRead,
)
from app.modules.pricing.services.base import PricingService


class DefaultPricingService(PricingService):
    def __init__(self, repository: PricingRepository, catalog_repository: CatalogRepository) -> None:
        self._repository = repository
        self._catalog_repository = catalog_repository

    def create_rule(self, payload: PricingRuleCreate) -> PricingRuleRead:
        created = self._repository.create_rule(PricingRule(id=0, **payload.model_dump()))
        return PricingRuleRead.model_validate(created.__dict__)

    def list_rules(self) -> list[PricingRuleRead]:
        return [PricingRuleRead.model_validate(rule.__dict__) for rule in self._repository.list_rules()]

    def calculate_price(self, payload: PriceCalculateRequest) -> PriceCalculateResponse:
        variant = self._catalog_repository.get_variant(payload.variant_id)
        if variant is None:
            raise ValueError("variant not found")
        product = self._catalog_repository.get_product(variant.product_id)
        if product is None:
            raise ValueError("product not found")

        base_price = variant.base_price if variant.base_price is not None else product.base_price
        calc = self._apply_rules(base_price, payload.qty, product.id, variant.id, payload.promo_code)
        return PriceCalculateResponse(
            unit_price=calc.unit_price,
            total_price=calc.total_price,
            applied_rules=[AppliedRuleRead.model_validate(rule.__dict__) for rule in calc.applied_rules],
        )

    def _apply_rules(
        self,
        base_price: Decimal,
        qty: int,
        product_id: int,
        variant_id: int,
        promo_code: str | None,
    ) -> PriceCalculation:
        price = base_price
        trace: list[AppliedRule] = []
        rules = sorted(self._repository.list_rules(), key=lambda rule: rule.priority)
        for rule in rules:
            if not rule.active or qty < rule.min_qty:
                continue
            if rule.product_id is not None and rule.product_id != product_id:
                continue
            if rule.variant_id is not None and rule.variant_id != variant_id:
                continue
            if rule.coupon_code is not None and rule.coupon_code != promo_code:
                continue

            if rule.rule_type == "percent":
                delta = -(price * rule.value / Decimal("100"))
            elif rule.rule_type == "fixed":
                delta = -rule.value
            else:
                continue

            price = max(Decimal("0.00"), price + delta)
            trace.append(AppliedRule(rule_id=rule.id, name=rule.name, delta=delta))

        return PriceCalculation(unit_price=price, total_price=price * qty, applied_rules=trace)