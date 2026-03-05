from app.modules.catalog.models.entity import CatalogEntity
from app.modules.catalog.repositories.base import CatalogRepository


class InMemoryCatalogRepository(CatalogRepository):
    def __init__(self) -> None:
        self._items: dict[int, CatalogEntity] = {}
        self._next_id = 1

    def list(self) -> list[CatalogEntity]:
        return list(self._items.values())

    def get(self, item_id: int) -> CatalogEntity | None:
        return self._items.get(item_id)

    def create(self, name: str) -> CatalogEntity:
        item = CatalogEntity(id=self._next_id, name=name)
        self._items[item.id] = item
        self._next_id += 1
        return item

    def update(self, item_id: int, name: str) -> CatalogEntity | None:
        item = self._items.get(item_id)
        if item is None:
            return None
        item.name = name
        return item

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None
