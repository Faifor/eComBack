from app.modules.ai.models.entity import AiEntity
from app.modules.ai.repositories.base import AiRepository


class InMemoryAiRepository(AiRepository):
    def __init__(self) -> None:
        self._items: dict[int, AiEntity] = {}
        self._next_id = 1

    def list(self) -> list[AiEntity]:
        return list(self._items.values())

    def get(self, item_id: int) -> AiEntity | None:
        return self._items.get(item_id)

    def create(self, name: str) -> AiEntity:
        item = AiEntity(id=self._next_id, name=name)
        self._items[item.id] = item
        self._next_id += 1
        return item

    def update(self, item_id: int, name: str) -> AiEntity | None:
        item = self._items.get(item_id)
        if item is None:
            return None
        item.name = name
        return item

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None
