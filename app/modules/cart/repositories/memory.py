from app.modules.cart.models.entity import CartEntity
from app.modules.cart.repositories.base import CartRepository


class InMemoryCartRepository(CartRepository):
    def __init__(self) -> None:
        self._items: dict[int, CartEntity] = {}
        self._next_id = 1

    def list(self) -> list[CartEntity]:
        return list(self._items.values())

    def get(self, item_id: int) -> CartEntity | None:
        return self._items.get(item_id)

    def create(self, name: str) -> CartEntity:
        item = CartEntity(id=self._next_id, name=name)
        self._items[item.id] = item
        self._next_id += 1
        return item

    def update(self, item_id: int, name: str) -> CartEntity | None:
        item = self._items.get(item_id)
        if item is None:
            return None
        item.name = name
        return item

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None