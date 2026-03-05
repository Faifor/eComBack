import uuid

from app.modules.cart.repositories.base import CartRepository
from app.modules.orders.models.entity import OrderStatus, OrderStatusHistoryEntry, PaymentMethod
from app.modules.orders.repositories.base import OrdersRepository
from app.modules.orders.schemas.dto import CheckoutRequest, OrderItemRead, OrderRead, OrderStatusHistoryRead
from app.modules.orders.services.base import OrdersService
from app.modules.payments.services.yookassa_client import YooKassaClient


class DefaultOrdersService(OrdersService):
    def __init__(self, repository: OrdersRepository, cart_repository: CartRepository, yookassa_client: YooKassaClient) -> None:
        self._repository = repository
        self._cart_repository = cart_repository
        self._yookassa_client = yookassa_client

    async def checkout(self, payload: CheckoutRequest) -> OrderRead:
        cart = self._cart_repository.get_cart(payload.cart_id)
        if cart is None:
            raise ValueError("cart not found")
        if not cart.items:
            raise ValueError("cart is empty")

        initial_status = OrderStatus.awaiting_cod_payment if payload.payment_method == PaymentMethod.cod else OrderStatus.created
        order = self._repository.create_order(user_id=cart.user_id, status=initial_status, payment_method=payload.payment_method)
        order.status_history.append(OrderStatusHistoryEntry(from_status=None, to_status=initial_status))

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

        if payload.payment_method == PaymentMethod.yookassa:
            idempotence_key = str(uuid.uuid4())
            payment = await self._yookassa_client.create_payment_intent(
                amount=order.total_price,
                idempotence_key=idempotence_key,
                description=f"Order #{order.id}",
            )
            order.payment_id = payment.get("id")
            order.payment_status = payment.get("status")
        else:
            order.payment_status = "pending_cod"

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
    
    def mark_cod_paid(self, order_id: int) -> OrderRead | None:
        order = self._repository.get_order(order_id)
        if order is None:
            return None
        if order.payment_method != PaymentMethod.cod:
            raise ValueError("order payment method is not COD")
        order.payment_status = "succeeded"
        history = OrderStatusHistoryEntry(from_status=order.status, to_status=OrderStatus.paid)
        updated = self._repository.update_status(order_id, OrderStatus.paid, history)
        return self._to_read(updated) if updated else None

    def process_payment_webhook(self, payment_id: str, payment_status: str) -> OrderRead | None:
        order = self._repository.get_by_payment_id(payment_id)
        if order is None:
            return None

        order.payment_status = payment_status
        if payment_status == "succeeded":
            new_status = OrderStatus.paid
        elif payment_status == "canceled":
            new_status = OrderStatus.cancelled
        else:
            new_status = OrderStatus.payment_failed

        history = OrderStatusHistoryEntry(from_status=order.status, to_status=new_status)
        updated = self._repository.update_status(order.id, new_status, history)
        return self._to_read(updated) if updated else None

    def _to_read(self, order) -> OrderRead:
        return OrderRead(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            payment_method=order.payment_method,
            payment_id=order.payment_id,
            payment_status=order.payment_status,
            total_price=order.total_price,
            items=[OrderItemRead.model_validate(item.__dict__) for item in order.items],
            status_history=[OrderStatusHistoryRead.model_validate(item.__dict__) for item in order.status_history],
        )
    