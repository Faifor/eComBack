from fastapi import APIRouter, HTTPException, status
from app.modules.cart.repositories.memory import InMemoryCartRepository
from app.modules.cart.schemas.dto import CartCreate, CartRead, CartUpdate
from app.modules.cart.services.service import DefaultCartService


router = APIRouter(prefix='/cart', tags=['cart'])
_service = DefaultCartService(InMemoryCartRepository())


@router.get('/', response_model=list[CartRead])
def list_items() -> list[CartRead]:
    return _service.list()


@router.get('/{item_id}', response_model=CartRead)
def get_item(item_id: int) -> CartRead:
    item = _service.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='cart item not found')
    return item


@router.post('/', response_model=CartRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: CartCreate) -> CartRead:
    return _service.create(payload)


@router.put('/{item_id}', response_model=CartRead)
def update_item(item_id: int, payload: CartUpdate) -> CartRead:
    item = _service.update(item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='cart item not found')
    return item


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    deleted = _service.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='cart item not found')
