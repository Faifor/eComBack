from app.modules.admin.models.entity import AdminEntity
from app.modules.admin.repositories.base import AdminRepository


class InMemoryAdminRepository(AdminRepository):
    def __init__(self) -> None:
        self._items: dict[int, AdminEntity] = {}
        self._next_id = 1

    def list(self) -> list[AdminEntity]:
        return list(self._items.values())

    def get(self, item_id: int) -> AdminEntity | None:
        return self._items.get(item_id)

    def create(self, name: str) -> AdminEntity:
        item = AdminEntity(id=self._next_id, name=name)
        self._items[item.id] = item
        self._next_id += 1
        return item

    def update(self, item_id: int, name: str) -> AdminEntity | None:
        item = self._items.get(item_id)
        if item is None:
            return None
        item.name = name
        return item

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None
