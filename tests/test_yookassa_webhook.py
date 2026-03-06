import sys
import types
import hashlib
import hmac


def test_yookassa_webhook_signature_validation(monkeypatch):
    httpx_stub = types.ModuleType("httpx")
    httpx_stub.AsyncClient = object
    monkeypatch.setitem(sys.modules, "httpx", httpx_stub)
    import app.modules.payments.routers.router as payments_router

    monkeypatch.setattr(payments_router, "YOOKASSA_WEBHOOK_SECRET", "secret")
    body = b'{"object":{"id":"pay_1","status":"succeeded"}}'
    signature = hmac.new(b"secret", body, hashlib.sha256).hexdigest()

    assert payments_router._validate_webhook_secret(body, signature, None)
    assert payments_router._validate_webhook_secret(body, None, "secret")
    assert not payments_router._validate_webhook_secret(body, "bad", None)