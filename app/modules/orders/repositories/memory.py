from app.modules.orders.models.entity import OrdersEntity
from app.modules.orders.repositories.base import OrdersRepository


class InMemoryOrdersRepository(OrdersRepository):
    def __init__(self) -> None:
        self._items: dict[int, OrdersEntity] = {}
        self._next_id = 1

    def list(self) -> list[OrdersEntity]:
        return list(self._items.values())

    def get(self, item_id: int) -> OrdersEntity | None:
        return self._items.get(item_id)

    def create(self, name: str) -> OrdersEntity:
        item = OrdersEntity(id=self._next_id, name=name)
        self._items[item.id] = item
        self._next_id += 1
        return item

    def update(self, item_id: int, name: str) -> OrdersEntity | None:
        item = self._items.get(item_id)
        if item is None:
            return None
        item.name = name
        return item

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None