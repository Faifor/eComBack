from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


from app.modules.auth.models.entity import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.USER


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)

class ProfileUpdateRequest(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=32)

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str | None
    role: UserRole
    created_at: datetime


class AuthResponse(BaseModel):
    user: UserRead
    tokens: TokenPair