from __future__ import annotations

from decimal import Decimal

import httpx

from app.core.config import YOOKASSA_SANDBOX, YOOKASSA_SECRET_KEY, YOOKASSA_SHOP_ID


class YooKassaClient:
    def __init__(self) -> None:
        self._shop_id = YOOKASSA_SHOP_ID
        self._secret_key = YOOKASSA_SECRET_KEY
        self._base_url = "https://api.yookassa.ru/v3" if not YOOKASSA_SANDBOX else "https://api.yookassa.ru/v3"

    async def create_payment_intent(self, amount: Decimal, idempotence_key: str, description: str) -> dict:
        if not self._shop_id or not self._secret_key:
            raise ValueError("YooKassa credentials are not configured")

        payload = {
            "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
            "capture": True,
            "confirmation": {"type": "redirect", "return_url": "https://example.com/payment/return"},
            "description": description,
        }
        headers = {"Idempotence-Key": idempotence_key}

        async with httpx.AsyncClient(base_url=self._base_url, timeout=15.0, auth=(self._shop_id, self._secret_key)) as client:
            response = await client.post("/payments", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()