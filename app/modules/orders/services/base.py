from abc import ABC, abstractmethod

from app.modules.orders.models.entity import OrderStatus
from app.modules.orders.schemas.dto import CheckoutRequest, OrderRead

class OrdersService(ABC):
    @abstractmethod
    async def checkout(self, payload: CheckoutRequest) -> OrderRead: ...

    @abstractmethod
    def list_orders(self) -> list[OrderRead]: ...

    @abstractmethod
    def get_order(self, order_id: int) -> OrderRead | None: ...

    @abstractmethod
    def transition_status(self, order_id: int, new_status: OrderStatus) -> OrderRead | None: ...