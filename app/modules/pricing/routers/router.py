from fastapi import APIRouter, HTTPException, status
from app.modules.pricing.repositories.memory import InMemoryPricingRepository
from app.modules.pricing.schemas.dto import PricingCreate, PricingRead, PricingUpdate
from app.modules.pricing.services.service import DefaultPricingService


router = APIRouter(prefix='/pricing', tags=['pricing'])
_service = DefaultPricingService(InMemoryPricingRepository())


@router.get('/', response_model=list[PricingRead])
def list_items() -> list[PricingRead]:
    return _service.list()


@router.get('/{item_id}', response_model=PricingRead)
def get_item(item_id: int) -> PricingRead:
    item = _service.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='pricing item not found')
    return item


@router.post('/', response_model=PricingRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: PricingCreate) -> PricingRead:
    return _service.create(payload)


@router.put('/{item_id}', response_model=PricingRead)
def update_item(item_id: int, payload: PricingUpdate) -> PricingRead:
    item = _service.update(item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='pricing item not found')
    return item


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    deleted = _service.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='pricing item not found')
