from app.modules.pricing.models.entity import PricingEntity
from app.modules.pricing.repositories.base import PricingRepository


class InMemoryPricingRepository(PricingRepository):
    def __init__(self) -> None:
        self._items: dict[int, PricingEntity] = {}
        self._next_id = 1

    def list(self) -> list[PricingEntity]:
        return list(self._items.values())

    def get(self, item_id: int) -> PricingEntity | None:
        return self._items.get(item_id)

    def create(self, name: str) -> PricingEntity:
        item = PricingEntity(id=self._next_id, name=name)
        self._items[item.id] = item
        self._next_id += 1
        return item

    def update(self, item_id: int, name: str) -> PricingEntity | None:
        item = self._items.get(item_id)
        if item is None:
            return None
        item.name = name
        return item

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None