from abc import ABC, abstractmethod
from app.modules.orders.models.entity import OrdersEntity


class OrdersRepository(ABC):
    @abstractmethod
    def list(self) -> list[OrdersEntity]: ...

    @abstractmethod
    def get(self, item_id: int) -> OrdersEntity | None: ...

    @abstractmethod
    def create(self, name: str) -> OrdersEntity: ...

    @abstractmethod
    def update(self, item_id: int, name: str) -> OrdersEntity | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...
