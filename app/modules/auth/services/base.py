from abc import ABC, abstractmethod
from app.modules.auth.schemas.dto import AuthCreate, AuthRead, AuthUpdate


class AuthService(ABC):
    @abstractmethod
    def list(self) -> list[AuthRead]: ...

    @abstractmethod
    def get(self, item_id: int) -> AuthRead | None: ...

    @abstractmethod
    def create(self, payload: AuthCreate) -> AuthRead: ...

    @abstractmethod
    def update(self, item_id: int, payload: AuthUpdate) -> AuthRead | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...