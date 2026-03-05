from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


class OrderStatus(str, Enum):
    created = "created"
    confirmed = "confirmed"
    awaiting_cod_payment = "awaiting_cod_payment"
    paid = "paid"
    payment_failed = "payment_failed"
    cancelled = "cancelled"
    shipped = "shipped"
    completed = "completed"

class PaymentMethod(str, Enum):
    yookassa = "yookassa"
    cod = "cod"


@dataclass
class OrderStatusHistoryEntry:
    from_status: OrderStatus | None
    to_status: OrderStatus
    changed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class OrderItem:
    id: int
    order_id: int
    sku: str
    title: str
    qty: int
    unit_price: Decimal
    line_total: Decimal
    rule_trace: list[dict] = field(default_factory=list)


@dataclass
class Order:
    id: int
    user_id: int
    status: OrderStatus
    payment_method: PaymentMethod
    payment_id: str | None = None
    payment_status: str | None = None
    items: list[OrderItem] = field(default_factory=list)
    total_price: Decimal = Decimal("0.00")
    status_history: list[OrderStatusHistoryEntry] = field(default_factory=list)