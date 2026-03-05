from abc import ABC, abstractmethod

from app.modules.auth.models.entity import User
from app.modules.auth.schemas.dto import AuthResponse, LoginRequest, RegisterRequest

class AuthService(ABC):
    @abstractmethod
    async def register(self, payload: RegisterRequest) -> AuthResponse: ...

    @abstractmethod
    async def login(self, payload: LoginRequest) -> AuthResponse: ...

    @abstractmethod
    async def refresh(self, refresh_token: str) -> AuthResponse: ...

    @abstractmethod
    async def me(self, user_id: int) -> User | None: ...