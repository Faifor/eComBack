from abc import ABC, abstractmethod

from app.modules.auth.repositories import UserProfile
from app.modules.auth.schemas.dto import AuthResponse, LoginRequest, ProfileUpdateRequest, RegisterRequest, UserRead

class AuthService(ABC):
    @abstractmethod
    async def register(self, payload: RegisterRequest) -> AuthResponse: ...

    @abstractmethod
    async def login(self, payload: LoginRequest) -> AuthResponse: ...

    @abstractmethod
    async def refresh(self, refresh_token: str) -> AuthResponse: ...

    @abstractmethod
    async def me(self, user_id: int) -> UserProfile | None: ...

    @abstractmethod
    async def update_profile(self, user_id: int, payload: ProfileUpdateRequest) -> UserRead: ...