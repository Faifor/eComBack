from abc import ABC, abstractmethod
from app.modules.orders.models.entity import Order, OrderItem, OrderStatus, OrderStatusHistoryEntry


class OrdersRepository(ABC):
    @abstractmethod
    def create_order(self, user_id: int, status: OrderStatus) -> Order: ...

    @abstractmethod
    def get_order(self, order_id: int) -> Order | None: ...

    @abstractmethod
    def add_order_item(self, order_id: int, sku: str, title: str, qty: int, unit_price, line_total, rule_trace) -> OrderItem: ...

    @abstractmethod
    def update_status(self, order_id: int, status: OrderStatus, history: OrderStatusHistoryEntry) -> Order | None: ...

    @abstractmethod
    def list_orders(self) -> list[Order]: ...
