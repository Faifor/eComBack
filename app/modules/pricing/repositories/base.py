from abc import ABC, abstractmethod
from app.modules.pricing.models.entity import PricingEntity


class PricingRepository(ABC):
    @abstractmethod
    def list(self) -> list[PricingEntity]: ...

    @abstractmethod
    def get(self, item_id: int) -> PricingEntity | None: ...

    @abstractmethod
    def create(self, name: str) -> PricingEntity: ...

    @abstractmethod
    def update(self, item_id: int, name: str) -> PricingEntity | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...
