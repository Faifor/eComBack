from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.errors import add_exception_handlers
from app.core.logging import RequestIdMiddleware, setup_logging

setup_logging()
app = FastAPI(
    title="eComBack",
    openapi_tags=[
        {"name": "auth", "description": "Пользовательская аутентификация и профиль."},
        {"name": "catalog", "description": "Пользовательский каталог: чтение и отзывы."},
        {"name": "cart", "description": "Пользовательская корзина."},
        {"name": "orders", "description": "Пользовательские заказы и checkout."},
        {"name": "payments", "description": "Сервисные платежные webhook-эндпоинты."},
        {"name": "admin", "description": "Админ-панель: управление каталогом, импорт, bulk-операции, отчеты."},
        {"name": "ai", "description": "AI-эндпоинты (отдельный модуль)."},
    ],
)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_exception_handlers(app)

app.include_router(api_v1_router)