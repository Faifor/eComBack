from app.modules.orders.repositories.base import OrdersRepository
from app.modules.orders.schemas.dto import OrdersCreate, OrdersRead, OrdersUpdate
from app.modules.orders.services.base import OrdersService


class DefaultOrdersService(OrdersService):
    def __init__(self, repository: OrdersRepository) -> None:
        self._repository = repository

    def list(self) -> list[OrdersRead]:
        return [OrdersRead(id=item.id, name=item.name) for item in self._repository.list()]

    def get(self, item_id: int) -> OrdersRead | None:
        item = self._repository.get(item_id)
        if item is None:
            return None
        return OrdersRead(id=item.id, name=item.name)

    def create(self, payload: OrdersCreate) -> OrdersRead:
        item = self._repository.create(name=payload.name)
        return OrdersRead(id=item.id, name=item.name)

    def update(self, item_id: int, payload: OrdersUpdate) -> OrdersRead | None:
        current = self._repository.get(item_id)
        if current is None:
            return None

        name = payload.name if payload.name is not None else current.name
        item = self._repository.update(item_id=item_id, name=name)
        if item is None:
            return None
        return OrdersRead(id=item.id, name=item.name)

    def delete(self, item_id: int) -> bool:
        return self._repository.delete(item_id)
    