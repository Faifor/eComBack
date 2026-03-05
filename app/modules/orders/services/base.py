from abc import ABC, abstractmethod
from app.modules.orders.schemas.dto import OrdersCreate, OrdersRead, OrdersUpdate


class OrdersService(ABC):
    @abstractmethod
    def list(self) -> list[OrdersRead]: ...

    @abstractmethod
    def get(self, item_id: int) -> OrdersRead | None: ...

    @abstractmethod
    def create(self, payload: OrdersCreate) -> OrdersRead: ...

    @abstractmethod
    def update(self, item_id: int, payload: OrdersUpdate) -> OrdersRead | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...