from __future__ import annotations

from base64 import urlsafe_b64encode
from hashlib import sha256

from cryptography.fernet import Fernet


class PersonalDataEncryptionService:
    def __init__(self, key: str) -> None:
        normalized_key = self._normalize_key(key)
        self._fernet = Fernet(normalized_key)

    def encrypt(self, value: str | None) -> str | None:
        if value is None:
            return None
        return self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt(self, value: str | None) -> str | None:
        if value is None:
            return None
        return self._fernet.decrypt(value.encode("utf-8")).decode("utf-8")

    @staticmethod
    def _normalize_key(key: str) -> bytes:
        candidate = key.encode("utf-8")
        if len(candidate) == 44:
            try:
                Fernet(candidate)
                return candidate
            except Exception:
                pass
        return urlsafe_b64encode(sha256(candidate).digest())