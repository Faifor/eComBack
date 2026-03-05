from fastapi import APIRouter, HTTPException, status
from app.modules.payments.repositories.memory import InMemoryPaymentsRepository
from app.modules.payments.schemas.dto import PaymentsCreate, PaymentsRead, PaymentsUpdate
from app.modules.payments.services.service import DefaultPaymentsService


router = APIRouter(prefix='/payments', tags=['payments'])
_service = DefaultPaymentsService(InMemoryPaymentsRepository())


@router.get('/', response_model=list[PaymentsRead])
def list_items() -> list[PaymentsRead]:
    return _service.list()


@router.get('/{item_id}', response_model=PaymentsRead)
def get_item(item_id: int) -> PaymentsRead:
    item = _service.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='payments item not found')
    return item


@router.post('/', response_model=PaymentsRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: PaymentsCreate) -> PaymentsRead:
    return _service.create(payload)


@router.put('/{item_id}', response_model=PaymentsRead)
def update_item(item_id: int, payload: PaymentsUpdate) -> PaymentsRead:
    item = _service.update(item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='payments item not found')
    return item


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    deleted = _service.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='payments item not found')