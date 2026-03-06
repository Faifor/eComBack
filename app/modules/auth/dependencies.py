from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import (
    AUTH_RATE_LIMIT_MAX_ATTEMPTS,
    AUTH_RATE_LIMIT_WINDOW_SECONDS,
    PERSONAL_DATA_ENC_KEY,
    REDIS_URL,
)
from app.core.security import PersonalDataEncryptionService
from app.db.session import get_db
from app.modules.auth.models.entity import UserRole
from app.modules.auth.repositories import UserProfile, UserRepository
from app.modules.auth.services.jwt import decode_access_token

security = HTTPBearer(auto_error=True)
_redis_client: Redis | None = None


async def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception as exc:
        raise unauthorized from exc

    if payload.get("type") != "access" or payload.get("sub") is None:
        raise unauthorized

    repository = UserRepository(db, PersonalDataEncryptionService(PERSONAL_DATA_ENC_KEY))
    user = await repository.get_by_id(int(payload["sub"]))
    if user is None:
        raise unauthorized
    return user


def require_role(*roles: UserRole):
    async def _dependency(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return _dependency


def auth_rate_limit(action: str):
    async def _dependency(request: Request, redis: Redis = Depends(get_redis)) -> None:
        ip = request.client.host if request.client else "unknown"
        key = f"auth:rate_limit:{action}:{ip}"
        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, AUTH_RATE_LIMIT_WINDOW_SECONDS)
        if current > AUTH_RATE_LIMIT_MAX_ATTEMPTS:
            ttl = await redis.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Retry in {max(ttl, 0)} seconds",
            )

    return _dependency


async def utcnow() -> datetime:
    return datetime.now(timezone.utc)