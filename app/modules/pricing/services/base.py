from abc import ABC, abstractmethod
from app.modules.pricing.schemas.dto import PriceCalculateRequest, PriceCalculateResponse, PricingRuleCreate, PricingRuleRead


class PricingService(ABC):
    @abstractmethod
    def create_rule(self, payload: PricingRuleCreate) -> PricingRuleRead: ...

    @abstractmethod
    def list_rules(self) -> list[PricingRuleRead]: ...

    @abstractmethod
    def calculate_price(self, payload: PriceCalculateRequest) -> PriceCalculateResponse: ...