from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import JWT_REFRESH_EXPIRE_DAYS
from app.modules.auth.models.entity import RefreshSession, User
from app.modules.auth.schemas.dto import AuthResponse, LoginRequest, RegisterRequest, TokenPair, UserRead
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

    async def register(self, payload: RegisterRequest) -> AuthResponse:
        existing = await self._db.execute(select(User).where(User.email == payload.email))
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            role=payload.role,
        )
        self._db.add(user)
        await self._db.flush()
        tokens = await self._issue_tokens(user)
        await self._db.commit()
        await self._db.refresh(user)
        return AuthResponse(user=_to_user_read(user), tokens=tokens)

    async def login(self, payload: LoginRequest) -> AuthResponse:
        result = await self._db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
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

        now = datetime.now(UTC)
        if session.expires_at <= now:
            raise unauthorized

        if not verify_password(refresh_token, session.token_hash):
            raise unauthorized

        user_result = await self._db.execute(select(User).where(User.id == session.user_id))
        user = user_result.scalar_one_or_none()
        if user is None:
            raise unauthorized
        
        session.is_revoked = True
        session.revoked_at = now
        session.last_used_at = now

        tokens = await self._issue_tokens(user, rotated_from_id=session.id)
        await self._db.commit()
        return AuthResponse(user=_to_user_read(user), tokens=tokens)

    async def me(self, user_id: int) -> User | None:
        result = await self._db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def _issue_tokens(self, user: User, rotated_from_id: int | None = None) -> TokenPair:
        session_expires = datetime.now(UTC) + timedelta(days=JWT_REFRESH_EXPIRE_DAYS)
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


def _to_user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        created_at=user.created_at,
    )