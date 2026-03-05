from fastapi import APIRouter, HTTPException, status
from app.modules.catalog.repositories.memory import InMemoryCatalogRepository
from app.modules.catalog.schemas.dto import CatalogCreate, CatalogRead, CatalogUpdate
from app.modules.catalog.services.service import DefaultCatalogService


router = APIRouter(prefix='/catalog', tags=['catalog'])
_service = DefaultCatalogService(InMemoryCatalogRepository())


@router.get('/', response_model=list[CatalogRead])
def list_items() -> list[CatalogRead]:
    return _service.list()


@router.get('/{item_id}', response_model=CatalogRead)
def get_item(item_id: int) -> CatalogRead:
    item = _service.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='catalog item not found')
    return item


@router.post('/', response_model=CatalogRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: CatalogCreate) -> CatalogRead:
    return _service.create(payload)


@router.put('/{item_id}', response_model=CatalogRead)
def update_item(item_id: int, payload: CatalogUpdate) -> CatalogRead:
    item = _service.update(item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='catalog item not found')
    return item


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    deleted = _service.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='catalog item not found')
