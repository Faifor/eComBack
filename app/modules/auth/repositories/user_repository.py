from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import PersonalDataEncryptionService
from app.modules.auth.models.entity import ProfileChangeLog, User, UserRole


@dataclass(slots=True)
class UserProfile:
    id: int
    email: str
    full_name: str
    phone: str | None
    role: UserRole
    hashed_password: str
    created_at: datetime


class UserRepository:
    def __init__(self, db: AsyncSession, encryption: PersonalDataEncryptionService) -> None:
        self._db = db
        self._encryption = encryption

    async def get_by_email(self, email: str) -> UserProfile | None:
        result = await self._db.execute(select(User).where(User.email_hash == _email_hash(email)))
        user = result.scalar_one_or_none()
        return self._to_profile(user) if user is not None else None

    async def get_by_id(self, user_id: int) -> UserProfile | None:
        result = await self._db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return self._to_profile(user) if user is not None else None

    async def create_user(
        self,
        *,
        email: str,
        full_name: str,
        phone: str | None,
        hashed_password: str,
        role: UserRole,
    ) -> UserProfile:
        user = User(
            email_enc=self._encryption.encrypt(email),
            email_hash=_email_hash(email),
            full_name_enc=self._encryption.encrypt(full_name),
            phone_enc=self._encryption.encrypt(phone),
            hashed_password=hashed_password,
            role=role,
        )
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return self._to_profile(user)

    async def update_profile(
        self,
        *,
        user_id: int,
        changed_by: int,
        email: str | None = None,
        full_name: str | None = None,
        phone: str | None = None,
    ) -> UserProfile | None:
        result = await self._db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            return None

        before = self._to_profile(user)
        diff: dict[str, dict[str, str | None]] = {}

        if email is not None and email != before.email:
            user.email_enc = self._encryption.encrypt(email)
            user.email_hash = _email_hash(email)
            diff["email"] = {"old": before.email, "new": email}

        if full_name is not None and full_name != before.full_name:
            user.full_name_enc = self._encryption.encrypt(full_name)
            diff["full_name"] = {"old": before.full_name, "new": full_name}

        if phone is not None and phone != before.phone:
            user.phone_enc = self._encryption.encrypt(phone)
            diff["phone"] = {"old": before.phone, "new": phone}

        if diff:
            self._db.add(
                ProfileChangeLog(
                    user_id=user_id,
                    changed_by=changed_by,
                    changed_at=datetime.now(timezone.utc),
                    diff=diff,
                )
            )

        await self._db.flush()
        await self._db.refresh(user)
        return self._to_profile(user)

    def _to_profile(self, user: User) -> UserProfile:
        return UserProfile(
            id=user.id,
            email=self._encryption.decrypt(user.email_enc) or "",
            full_name=self._encryption.decrypt(user.full_name_enc) or "",
            phone=self._encryption.decrypt(user.phone_enc),
            role=user.role,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )


def _email_hash(email: str) -> str:
    return sha256(email.strip().lower().encode("utf-8")).hexdigest()