from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL
from app.db.base import Base


def _sync_url(url: str) -> str:
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+psycopg://", 1)
    if url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    return url


sync_engine = create_engine(_sync_url(DATABASE_URL), future=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)


def init_sync_db() -> None:
    Base.metadata.create_all(bind=sync_engine)