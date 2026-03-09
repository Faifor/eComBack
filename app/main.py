from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.errors import add_exception_handlers
from app.core.logging import RequestIdMiddleware, setup_logging

setup_logging()
app = FastAPI(
    title="eComBack",
    openapi_tags=[
        {"name": "auth", "description": "Авторизация и профиль пользователя."},
        {"name": "catalog-user", "description": "Каталог для витрины/пользователя (без админских операций)."},
        {"name": "cart", "description": "Корзина пользователя."},
        {"name": "orders-user", "description": "Заказы пользователя: checkout и просмотр."},
        {"name": "orders-admin", "description": "Админские операции по заказам."},
        {"name": "admin", "description": "Каноничные ручки админ-панели."},
        {"name": "pricing", "description": "Технический pricing API (admin/integration)."},
        {"name": "payments", "description": "Сервисные платежные вебхуки."},
        {"name": "ai", "description": "AI-модуль."},
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