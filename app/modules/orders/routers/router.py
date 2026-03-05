from fastapi import APIRouter, HTTPException, status
from app.modules.orders.repositories.memory import InMemoryOrdersRepository
from app.modules.orders.schemas.dto import OrdersCreate, OrdersRead, OrdersUpdate
from app.modules.orders.services.service import DefaultOrdersService


router = APIRouter(prefix='/orders', tags=['orders'])
_service = DefaultOrdersService(InMemoryOrdersRepository())


@router.get('/', response_model=list[OrdersRead])
def list_items() -> list[OrdersRead]:
    return _service.list()


@router.get('/{item_id}', response_model=OrdersRead)
def get_item(item_id: int) -> OrdersRead:
    item = _service.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='orders item not found')
    return item


@router.post('/', response_model=OrdersRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: OrdersCreate) -> OrdersRead:
    return _service.create(payload)


@router.put('/{item_id}', response_model=OrdersRead)
def update_item(item_id: int, payload: OrdersUpdate) -> OrdersRead:
    item = _service.update(item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='orders item not found')
    return item


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    deleted = _service.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='orders item not found')
