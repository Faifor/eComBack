from fastapi import APIRouter, HTTPException, status
from app.modules.auth.repositories.memory import InMemoryAuthRepository
from app.modules.auth.schemas.dto import AuthCreate, AuthRead, AuthUpdate
from app.modules.auth.services.service import DefaultAuthService


router = APIRouter(prefix='/auth', tags=['auth'])
_service = DefaultAuthService(InMemoryAuthRepository())


@router.get('/', response_model=list[AuthRead])
def list_items() -> list[AuthRead]:
    return _service.list()


@router.get('/{item_id}', response_model=AuthRead)
def get_item(item_id: int) -> AuthRead:
    item = _service.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='auth item not found')
    return item


@router.post('/', response_model=AuthRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: AuthCreate) -> AuthRead:
    return _service.create(payload)


@router.put('/{item_id}', response_model=AuthRead)
def update_item(item_id: int, payload: AuthUpdate) -> AuthRead:
    item = _service.update(item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='auth item not found')
    return item


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    deleted = _service.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='auth item not found')