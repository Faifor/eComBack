from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from app.modules.orders.models.entity import OrderStatus


class CheckoutRequest(BaseModel):
    cart_id: int

class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemRead(BaseModel):
    id: int
    order_id: int
    sku: str
    title: str
    qty: int
    unit_price: Decimal
    line_total: Decimal
    rule_trace: list[dict]


class OrderStatusHistoryRead(BaseModel):
    from_status: OrderStatus | None
    to_status: OrderStatus
    changed_at: datetime


class OrderRead(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_price: Decimal
    items: list[OrderItemRead]
    status_history: list[OrderStatusHistoryRead]
