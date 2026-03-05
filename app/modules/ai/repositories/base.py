from abc import ABC, abstractmethod
from app.modules.ai.models.entity import AiEntity


class AiRepository(ABC):
    @abstractmethod
    def list(self) -> list[AiEntity]: ...

    @abstractmethod
    def get(self, item_id: int) -> AiEntity | None: ...

    @abstractmethod
    def create(self, name: str) -> AiEntity: ...

    @abstractmethod
    def update(self, item_id: int, name: str) -> AiEntity | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...