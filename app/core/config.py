from __future__ import annotations

import os

from pydantic import BaseModel, Field, ValidationError, field_validator


class Settings(BaseModel):
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "app_db"
    postgres_host: str = "db"
    postgres_port: int = 5432

    database_url: str | None = None

    jwt_secret: str = "change-me-access"
    jwt_refresh_secret: str = "change-me-refresh"
    jwt_access_expire_minutes: int = Field(default=15, ge=1)
    jwt_refresh_expire_days: int = Field(default=30, ge=1)

    redis_url: str = "redis://redis:6379/0"
    auth_rate_limit_max_attempts: int = Field(default=5, ge=1)
    auth_rate_limit_window_seconds: int = Field(default=60, ge=1)

    personal_data_enc_key: str = "change-me-personal-data"

    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""
    yookassa_sandbox: bool = True
    yookassa_webhook_secret: str = ""

    @classmethod
    def from_env(cls) -> "Settings":
        raw = {
            "postgres_user": os.getenv("POSTGRES_USER", "postgres"),
            "postgres_password": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "postgres_db": os.getenv("POSTGRES_DB", "app_db"),
            "postgres_host": os.getenv("POSTGRES_HOST", "db"),
            "postgres_port": os.getenv("POSTGRES_PORT", "5432"),
            "database_url": os.getenv("DATABASE_URL") or None,
            "jwt_secret": os.getenv("JWT_SECRET", "change-me-access"),
            "jwt_refresh_secret": os.getenv("JWT_REFRESH_SECRET", "change-me-refresh"),
            "jwt_access_expire_minutes": os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "15"),
            "jwt_refresh_expire_days": os.getenv("JWT_REFRESH_EXPIRE_DAYS", "30"),
            "redis_url": os.getenv("REDIS_URL", "redis://redis:6379/0"),
            "auth_rate_limit_max_attempts": os.getenv("AUTH_RATE_LIMIT_MAX_ATTEMPTS", "5"),
            "auth_rate_limit_window_seconds": os.getenv("AUTH_RATE_LIMIT_WINDOW_SECONDS", "60"),
            "personal_data_enc_key": os.getenv("PERSONAL_DATA_ENC_KEY", "change-me-personal-data"),
            "yookassa_shop_id": os.getenv("YOOKASSA_SHOP_ID", ""),
            "yookassa_secret_key": os.getenv("YOOKASSA_SECRET_KEY", ""),
            "yookassa_sandbox": os.getenv("YOOKASSA_SANDBOX", "true"),
            "yookassa_webhook_secret": os.getenv("YOOKASSA_WEBHOOK_SECRET", ""),
        }
        return cls.model_validate(raw)

    @field_validator("yookassa_sandbox", mode="before")
    @classmethod
    def _coerce_bool(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"1", "true", "yes", "on"}

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

try:
    settings = Settings.from_env()
except ValidationError as exc:  # pragma: no cover
    raise RuntimeError(f"Invalid application configuration: {exc}") from exc

DATABASE_URL = settings.resolved_database_url
JWT_SECRET = settings.jwt_secret
JWT_REFRESH_SECRET = settings.jwt_refresh_secret
JWT_ACCESS_EXPIRE_MINUTES = settings.jwt_access_expire_minutes
JWT_REFRESH_EXPIRE_DAYS = settings.jwt_refresh_expire_days
REDIS_URL = settings.redis_url
AUTH_RATE_LIMIT_MAX_ATTEMPTS = settings.auth_rate_limit_max_attempts
AUTH_RATE_LIMIT_WINDOW_SECONDS = settings.auth_rate_limit_window_seconds
PERSONAL_DATA_ENC_KEY = settings.personal_data_enc_key
YOOKASSA_SHOP_ID = settings.yookassa_shop_id
YOOKASSA_SECRET_KEY = settings.yookassa_secret_key
YOOKASSA_SANDBOX = settings.yookassa_sandbox
YOOKASSA_WEBHOOK_SECRET = settings.yookassa_webhook_secret