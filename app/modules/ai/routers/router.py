from fastapi import APIRouter, HTTPException, Response, status
from app.modules.ai.repositories.memory import InMemoryAiRepository
from app.modules.ai.schemas.dto import AiCreate, AiRead, AiUpdate
from app.modules.ai.services.service import DefaultAiService


router = APIRouter(prefix='/ai', tags=['ai'])
_service = DefaultAiService(InMemoryAiRepository())


@router.get('/', response_model=list[AiRead])
def list_items() -> list[AiRead]:
    return _service.list()


@router.get('/{item_id}', response_model=AiRead)
def get_item(item_id: int) -> AiRead:
    item = _service.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ai item not found')
    return item


@router.post('/', response_model=AiRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: AiCreate) -> AiRead:
    return _service.create(payload)


@router.put('/{item_id}', response_model=AiRead)
def update_item(item_id: int, payload: AiUpdate) -> AiRead:
    item = _service.update(item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ai item not found')
    return item


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_item(item_id: int) -> None:
    deleted = _service.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ai item not found')