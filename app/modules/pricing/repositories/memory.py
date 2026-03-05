from app.modules.pricing.models.entity import PricingRule
from app.modules.pricing.repositories.base import PricingRepository


class InMemoryPricingRepository(PricingRepository):
    def __init__(self) -> None:
        self._rules: dict[int, PricingRule] = {}
        self._next_id = 1

    def create_rule(self, rule: PricingRule) -> PricingRule:
        rule.id = self._next_id
        self._rules[rule.id] = rule
        self._next_id += 1
        return rule

    def list_rules(self) -> list[PricingRule]:
        return list(self._rules.values())