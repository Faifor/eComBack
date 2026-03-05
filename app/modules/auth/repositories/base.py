from abc import ABC, abstractmethod
from app.modules.auth.models.entity import AuthEntity


class AuthRepository(ABC):
    @abstractmethod
    def list(self) -> list[AuthEntity]: ...

    @abstractmethod
    def get(self, item_id: int) -> AuthEntity | None: ...

    @abstractmethod
    def create(self, name: str) -> AuthEntity: ...

    @abstractmethod
    def update(self, item_id: int, name: str) -> AuthEntity | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...