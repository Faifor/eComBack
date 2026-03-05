from abc import ABC, abstractmethod
from app.modules.ai.schemas.dto import AiCreate, AiRead, AiUpdate


class AiService(ABC):
    @abstractmethod
    def list(self) -> list[AiRead]: ...

    @abstractmethod
    def get(self, item_id: int) -> AiRead | None: ...

    @abstractmethod
    def create(self, payload: AiCreate) -> AiRead: ...

    @abstractmethod
    def update(self, item_id: int, payload: AiUpdate) -> AiRead | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...