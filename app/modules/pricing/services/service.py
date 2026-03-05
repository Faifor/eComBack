from app.modules.pricing.repositories.base import PricingRepository
from app.modules.pricing.schemas.dto import PricingCreate, PricingRead, PricingUpdate
from app.modules.pricing.services.base import PricingService


class DefaultPricingService(PricingService):
    def __init__(self, repository: PricingRepository) -> None:
        self._repository = repository

    def list(self) -> list[PricingRead]:
        return [PricingRead(id=item.id, name=item.name) for item in self._repository.list()]

    def get(self, item_id: int) -> PricingRead | None:
        item = self._repository.get(item_id)
        if item is None:
            return None
        return PricingRead(id=item.id, name=item.name)

    def create(self, payload: PricingCreate) -> PricingRead:
        item = self._repository.create(name=payload.name)
        return PricingRead(id=item.id, name=item.name)

    def update(self, item_id: int, payload: PricingUpdate) -> PricingRead | None:
        current = self._repository.get(item_id)
        if current is None:
            return None

        name = payload.name if payload.name is not None else current.name
        item = self._repository.update(item_id=item_id, name=name)
        if item is None:
            return None
        return PricingRead(id=item.id, name=item.name)

    def delete(self, item_id: int) -> bool:
        return self._repository.delete(item_id)
