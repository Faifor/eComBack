from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.dependencies import require_role
from app.modules.auth.models.entity import UserRole
from app.modules.orders.schemas.dto import CheckoutRequest, OrderRead, OrderStatusUpdate
from app.modules.orders.services.service import DefaultOrdersService
from app.modules.payments.services.yookassa_client import YooKassaClient
from app.modules.runtime import cart_repository, orders_repository


router = APIRouter(prefix="/orders", tags=["orders"])
_service = DefaultOrdersService(orders_repository, cart_repository, YooKassaClient())


@router.post("/checkout", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def checkout(payload: CheckoutRequest) -> OrderRead:
    try:
        return await _service.checkout(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/", response_model=list[OrderRead])
def list_orders() -> list[OrderRead]:
    return _service.list_orders()


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int) -> OrderRead:
    order = _service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    return order


@router.post("/{order_id}/status", response_model=OrderRead)
def update_order_status(order_id: int, payload: OrderStatusUpdate) -> OrderRead:
    order = _service.transition_status(order_id, payload.status)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    return order


@router.post("/{order_id}/cod/confirm", response_model=OrderRead, dependencies=[Depends(require_role(UserRole.ADMIN))])
def confirm_cod_payment(order_id: int) -> OrderRead:
    try:
        order = _service.mark_cod_paid(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    return order