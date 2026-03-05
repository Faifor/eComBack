from app.modules.payments.models.entity import PaymentsEntity
from app.modules.payments.repositories.base import PaymentsRepository


class InMemoryPaymentsRepository(PaymentsRepository):
    def __init__(self) -> None:
        self._items: dict[int, PaymentsEntity] = {}
        self._next_id = 1

    def list(self) -> list[PaymentsEntity]:
        return list(self._items.values())

    def get(self, item_id: int) -> PaymentsEntity | None:
        return self._items.get(item_id)

    def create(self, name: str) -> PaymentsEntity:
        item = PaymentsEntity(id=self._next_id, name=name)
        self._items[item.id] = item
        self._next_id += 1
        return item

    def update(self, item_id: int, name: str) -> PaymentsEntity | None:
        item = self._items.get(item_id)
        if item is None:
            return None
        item.name = name
        return item

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None
