from __future__ import annotations

from datetime import datetime, timezone, timedelta
from uuid import uuid4

import jwt

from app.core.config import JWT_ACCESS_EXPIRE_MINUTES, JWT_REFRESH_EXPIRE_DAYS, JWT_REFRESH_SECRET, JWT_SECRET


def _build_payload(*, subject: str, token_type: str, expires_delta: timedelta, extra: dict | None = None) -> dict:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    if extra:
        payload.update(extra)
    return payload


def create_access_token(subject: str, role: str) -> str:
    payload = _build_payload(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(minutes=JWT_ACCESS_EXPIRE_MINUTES),
        extra={"role": role},
    )
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def create_refresh_token(subject: str, session_id: int) -> str:
    payload = _build_payload(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(days=JWT_REFRESH_EXPIRE_DAYS),
        extra={"sid": session_id},
    )
    return jwt.encode(payload, JWT_REFRESH_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])


def decode_refresh_token(token: str) -> dict:
    return jwt.decode(token, JWT_REFRESH_SECRET, algorithms=["HS256"])