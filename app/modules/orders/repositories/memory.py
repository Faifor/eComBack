from decimal import Decimal

from app.modules.orders.models.entity import Order, OrderItem, OrderStatus, OrderStatusHistoryEntry, PaymentMethod
from app.modules.orders.repositories.base import OrdersRepository


class InMemoryOrdersRepository(OrdersRepository):
    def __init__(self) -> None:
        self._orders: dict[int, Order] = {}
        self._next_order_id = 1
        self._next_item_id = 1

    def create_order(self, user_id: int, status: OrderStatus, payment_method: PaymentMethod) -> Order:
        order = Order(
            id=self._next_order_id,
            user_id=user_id,
            status=status,
            payment_method=payment_method,
            total_price=Decimal("0.00"),
        )
        self._orders[order.id] = order
        self._next_order_id += 1
        return order

    def get_order(self, order_id: int) -> Order | None:
        return self._orders.get(order_id)
    
    def get_by_payment_id(self, payment_id: str) -> Order | None:
        for order in self._orders.values():
            if order.payment_id == payment_id:
                return order
        return None

    def add_order_item(self, order_id: int, sku: str, title: str, qty: int, unit_price, line_total, rule_trace) -> OrderItem:
        order = self._orders[order_id]
        item = OrderItem(
            id=self._next_item_id,
            order_id=order_id,
            sku=sku,
            title=title,
            qty=qty,
            unit_price=unit_price,
            line_total=line_total,
            rule_trace=rule_trace,
        )
        self._next_item_id += 1
        order.items.append(item)
        order.total_price += line_total
        return item

    def update_status(self, order_id: int, status: OrderStatus, history: OrderStatusHistoryEntry) -> Order | None:
        order = self._orders.get(order_id)
        if order is None:
            return None
        order.status = status
        order.status_history.append(history)
        return order

    def list_orders(self) -> list[Order]:
        return list(self._orders.values())