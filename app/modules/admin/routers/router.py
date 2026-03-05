from fastapi import APIRouter, HTTPException, status
from app.modules.admin.repositories.memory import InMemoryAdminRepository
from app.modules.admin.schemas.dto import AdminCreate, AdminRead, AdminUpdate
from app.modules.admin.services.service import DefaultAdminService


router = APIRouter(prefix='/admin', tags=['admin'])
_service = DefaultAdminService(InMemoryAdminRepository())


@router.get('/', response_model=list[AdminRead])
def list_items() -> list[AdminRead]:
    return _service.list()


@router.get('/{item_id}', response_model=AdminRead)
def get_item(item_id: int) -> AdminRead:
    item = _service.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='admin item not found')
    return item


@router.post('/', response_model=AdminRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: AdminCreate) -> AdminRead:
    return _service.create(payload)


@router.put('/{item_id}', response_model=AdminRead)
def update_item(item_id: int, payload: AdminUpdate) -> AdminRead:
    item = _service.update(item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='admin item not found')
    return item


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    deleted = _service.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='admin item not found')