from app.modules.auth.models.entity import AuthEntity
from app.modules.auth.repositories.base import AuthRepository


class InMemoryAuthRepository(AuthRepository):
    def __init__(self) -> None:
        self._items: dict[int, AuthEntity] = {}
        self._next_id = 1

    def list(self) -> list[AuthEntity]:
        return list(self._items.values())

    def get(self, item_id: int) -> AuthEntity | None:
        return self._items.get(item_id)

    def create(self, name: str) -> AuthEntity:
        item = AuthEntity(id=self._next_id, name=name)
        self._items[item.id] = item
        self._next_id += 1
        return item

    def update(self, item_id: int, name: str) -> AuthEntity | None:
        item = self._items.get(item_id)
        if item is None:
            return None
        item.name = name
        return item

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None