from app.modules.ai.repositories.base import AiRepository
from app.modules.ai.schemas.dto import AiCreate, AiRead, AiUpdate
from app.modules.ai.services.base import AiService


class DefaultAiService(AiService):
    def __init__(self, repository: AiRepository) -> None:
        self._repository = repository

    def list(self) -> list[AiRead]:
        return [AiRead(id=item.id, name=item.name) for item in self._repository.list()]

    def get(self, item_id: int) -> AiRead | None:
        item = self._repository.get(item_id)
        if item is None:
            return None
        return AiRead(id=item.id, name=item.name)

    def create(self, payload: AiCreate) -> AiRead:
        item = self._repository.create(name=payload.name)
        return AiRead(id=item.id, name=item.name)

    def update(self, item_id: int, payload: AiUpdate) -> AiRead | None:
        current = self._repository.get(item_id)
        if current is None:
            return None

        name = payload.name if payload.name is not None else current.name
        item = self._repository.update(item_id=item_id, name=name)
        if item is None:
            return None
        return AiRead(id=item.id, name=item.name)

    def delete(self, item_id: int) -> bool:
        return self._repository.delete(item_id)
