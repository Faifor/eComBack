from abc import ABC, abstractmethod
from app.modules.admin.models.entity import AdminEntity


class AdminRepository(ABC):
    @abstractmethod
    def list(self) -> list[AdminEntity]: ...

    @abstractmethod
    def get(self, item_id: int) -> AdminEntity | None: ...

    @abstractmethod
    def create(self, name: str) -> AdminEntity: ...

    @abstractmethod
    def update(self, item_id: int, name: str) -> AdminEntity | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...