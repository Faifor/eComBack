from __future__ import annotations

from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import JWT_REFRESH_EXPIRE_DAYS, PERSONAL_DATA_ENC_KEY
from app.core.security import PersonalDataEncryptionService
from app.modules.auth.models.entity import RefreshSession
from app.modules.auth.repositories import UserProfile, UserRepository
from app.modules.auth.schemas.dto import (
    AuthResponse,
    LoginRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    TokenPair,
    UserRead,
)
from app.modules.auth.services.base import AuthService

from app.modules.auth.services.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.modules.auth.services.password import hash_password, verify_password


class DatabaseAuthService(AuthService):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._users = UserRepository(db, PersonalDataEncryptionService(PERSONAL_DATA_ENC_KEY))

    async def register(self, payload: RegisterRequest) -> AuthResponse:
        existing = await self._users.get_by_email(payload.email)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        user = await self._users.create_user(
            email=payload.email,
            full_name=payload.full_name,
            phone=payload.phone,
            hashed_password=hash_password(payload.password),
            role=payload.role,
        )
        
        tokens = await self._issue_tokens(user)
        await self._db.commit()
        
        return AuthResponse(user=_to_user_read(user), tokens=tokens)

    async def login(self, payload: LoginRequest) -> AuthResponse:
        user = await self._users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        tokens = await self._issue_tokens(user)
        await self._db.commit()
        return AuthResponse(user=_to_user_read(user), tokens=tokens)

    async def refresh(self, refresh_token: str) -> AuthResponse:
        unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        try:
            payload = decode_refresh_token(refresh_token)
        except Exception as exc:
            raise unauthorized from exc

        if payload.get("type") != "refresh" or payload.get("sid") is None:
            raise unauthorized

        session_result = await self._db.execute(
            select(RefreshSession).where(RefreshSession.id == int(payload["sid"]))
        )
        session = session_result.scalar_one_or_none()
        if session is None or session.is_revoked:
            raise unauthorized

        now = datetime.now(timezone.utc)
        if session.expires_at <= now:
            raise unauthorized

        if not verify_password(refresh_token, session.token_hash):
            raise unauthorized

        user = await self._users.get_by_id(session.user_id)
        if user is None:
            raise unauthorized
        
        session.is_revoked = True
        session.revoked_at = now
        session.last_used_at = now

        tokens = await self._issue_tokens(user, rotated_from_id=session.id)
        await self._db.commit()
        return AuthResponse(user=_to_user_read(user), tokens=tokens)

    async def me(self, user_id: int) -> UserProfile | None:
        return await self._users.get_by_id(user_id)

    async def update_profile(self, user_id: int, payload: ProfileUpdateRequest) -> UserRead:
        user = await self._users.update_profile(
            user_id=user_id,
            changed_by=user_id,
            email=payload.email,
            full_name=payload.full_name,
            phone=payload.phone,
        )
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await self._db.commit()
        return _to_user_read(user)

    async def _issue_tokens(self, user: UserProfile, rotated_from_id: int | None = None) -> TokenPair:
        session_expires = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_EXPIRE_DAYS)
        session = RefreshSession(
            user_id=user.id,
            token_hash="pending",
            expires_at=session_expires,
            rotated_from_id=rotated_from_id,
        )
        self._db.add(session)
        await self._db.flush()

        refresh_token = create_refresh_token(str(user.id), session.id)
        session.token_hash = hash_password(refresh_token)
        access_token = create_access_token(str(user.id), user.role.value)

        return TokenPair(access_token=access_token, refresh_token=refresh_token)


def _to_user_read(user: UserProfile) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role,
        created_at=user.created_at,
    )