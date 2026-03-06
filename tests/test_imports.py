import importlib
import sys
import types


def test_key_modules_importable_with_httpx_stub(monkeypatch):
    httpx_stub = types.ModuleType("httpx")

    class DummyAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, *args, **kwargs):
            class Resp:
                def raise_for_status(self):
                    return None

                def json(self):
                    return {}

            return Resp()

    httpx_stub.AsyncClient = DummyAsyncClient
    monkeypatch.setitem(sys.modules, "httpx", httpx_stub)

    modules = [
        "app.core.config",
        "app.core.logging",
        "app.modules.auth.services.jwt",
        "app.modules.cart.services.service",
        "app.modules.orders.services.service",
        "app.modules.payments.routers.router",
    ]

    for module in modules:
        importlib.import_module(module)