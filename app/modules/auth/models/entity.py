from __future__ import annotations

from datetime import datetime
try:
    from enum import StrEnum
except ImportError:  # pragma: no cover
    from enum import Enum

    class StrEnum(str, Enum):
        pass


from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import TimestampedBase


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"
    MANAGER = "manager"
    SUPPORT = "support"


class User(TimestampedBase):
    __tablename__ = "users"

    email_enc: Mapped[str] = mapped_column(String(1024), nullable=False)
    email_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    full_name_enc: Mapped[str] = mapped_column(String(1024), nullable=False)
    phone_enc: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False),
        default=UserRole.USER,
        nullable=False,
    )


class RefreshSession(TimestampedBase):
    __tablename__ = "refresh_sessions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rotated_from_id: Mapped[int | None] = mapped_column(
        ForeignKey("refresh_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )


class ProfileChangeLog(TimestampedBase):
    __tablename__ = "profile_change_logs"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    diff: Mapped[dict[str, dict[str, str | None]]] = mapped_column(JSON, nullable=False)