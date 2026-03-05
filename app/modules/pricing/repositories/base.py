from abc import ABC, abstractmethod
from app.modules.pricing.models.entity import PricingRule


class PricingRepository(ABC):
    @abstractmethod
    def create_rule(self, rule: PricingRule) -> PricingRule: ...

    @abstractmethod
    def list_rules(self) -> list[PricingRule]: ...