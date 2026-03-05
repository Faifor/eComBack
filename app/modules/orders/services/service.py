from app.modules.cart.repositories.base import CartRepository
from app.modules.orders.models.entity import OrderStatus, OrderStatusHistoryEntry
from app.modules.orders.repositories.base import OrdersRepository
from app.modules.orders.schemas.dto import CheckoutRequest, OrderItemRead, OrderRead, OrderStatusHistoryRead
from app.modules.orders.services.base import OrdersService


class DefaultOrdersService(OrdersService):
    def __init__(self, repository: OrdersRepository, cart_repository: CartRepository) -> None:
        self._repository = repository
        self._cart_repository = cart_repository

    def checkout(self, payload: CheckoutRequest) -> OrderRead:
        cart = self._cart_repository.get_cart(payload.cart_id)
        if cart is None:
            raise ValueError("cart not found")
        if not cart.items:
            raise ValueError("cart is empty")

        order = self._repository.create_order(user_id=cart.user_id, status=OrderStatus.created)
        order.status_history.append(OrderStatusHistoryEntry(from_status=None, to_status=OrderStatus.created))

        for item in cart.items:
            self._repository.add_order_item(
                order_id=order.id,
                sku=item.sku,
                title=item.title,
                qty=item.qty,
                unit_price=item.unit_price,
                line_total=item.total_price,
                rule_trace=item.rule_trace,
            )
        return self._to_read(order)

    def list_orders(self) -> list[OrderRead]:
        return [self._to_read(order) for order in self._repository.list_orders()]

    def get_order(self, order_id: int) -> OrderRead | None:
        order = self._repository.get_order(order_id)
        return self._to_read(order) if order else None

    def transition_status(self, order_id: int, new_status: OrderStatus) -> OrderRead | None:
        order = self._repository.get_order(order_id)
        if order is None:
            return None
        history = OrderStatusHistoryEntry(from_status=order.status, to_status=new_status)
        updated = self._repository.update_status(order_id, new_status, history)
        return self._to_read(updated) if updated else None

    def _to_read(self, order) -> OrderRead:
        return OrderRead(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            total_price=order.total_price,
            items=[OrderItemRead.model_validate(item.__dict__) for item in order.items],
            status_history=[OrderStatusHistoryRead.model_validate(item.__dict__) for item in order.status_history],
        )
    