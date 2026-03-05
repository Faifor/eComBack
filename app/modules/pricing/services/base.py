from abc import ABC, abstractmethod
from app.modules.pricing.schemas.dto import PricingCreate, PricingRead, PricingUpdate


class PricingService(ABC):
    @abstractmethod
    def list(self) -> list[PricingRead]: ...

    @abstractmethod
    def get(self, item_id: int) -> PricingRead | None: ...

    @abstractmethod
    def create(self, payload: PricingCreate) -> PricingRead: ...

    @abstractmethod
    def update(self, item_id: int, payload: PricingUpdate) -> PricingRead | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...