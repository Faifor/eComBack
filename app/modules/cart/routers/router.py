from fastapi import APIRouter, HTTPException, status

from app.modules.cart.schemas.dto import CartCreate, CartItemUpsert, CartRead
from app.modules.cart.services.service import DefaultCartService
from app.modules.runtime import cart_repository, catalog_repository, pricing_service


router = APIRouter(prefix="/cart", tags=["cart"])
_service = DefaultCartService(cart_repository, catalog_repository, pricing_service)


@router.post("/", response_model=CartRead, status_code=status.HTTP_201_CREATED)
def create_cart(payload: CartCreate) -> CartRead:
    return _service.create_cart(payload)


@router.get("/{cart_id}", response_model=CartRead)
def get_cart(cart_id: int) -> CartRead:
    cart = _service.get_cart(cart_id)
    if cart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="cart not found")
    return cart


@router.put("/{cart_id}/items/{variant_id}", response_model=CartRead)
def upsert_item(cart_id: int, variant_id: int, payload: CartItemUpsert) -> CartRead:
    payload.variant_id = variant_id
    try:
        return _service.upsert_item(cart_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc