from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db import sync_session
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models.entity import UserRole
from app.modules.auth.repositories.user_repository import UserProfile
from app.modules.cart.repositories.memory import InMemoryCartRepository
from app.modules.cart.services.service import DefaultCartService
from app.modules.catalog.repositories.sqlalchemy import SQLAlchemyCatalogRepository
from app.modules.catalog.services.service import DefaultCatalogService
from app.modules.orders.repositories.sqlalchemy import SQLAlchemyOrdersRepository
from app.modules.orders.services.service import DefaultOrdersService
from app.modules.pricing.repositories.sqlalchemy import SQLAlchemyPricingRepository
from app.modules.pricing.services.service import DefaultPricingService
from app.modules import runtime
from app.modules.admin.routers import router as admin_router
from app.modules.cart.routers import router as cart_router
from app.modules.orders.routers import router as orders_router


def test_admin_created_product_visible_in_catalog_and_checkout(tmp_path: Path) -> None:
    db_file = tmp_path / "integration.db"
    engine = create_engine(f"sqlite:///{db_file}", future=True)
    sync_session.sync_engine = engine
    sync_session.SyncSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    runtime.catalog_repository = SQLAlchemyCatalogRepository()
    runtime.pricing_repository = SQLAlchemyPricingRepository()
    runtime.cart_repository = InMemoryCartRepository()
    runtime.orders_repository = SQLAlchemyOrdersRepository()
    runtime.pricing_service = DefaultPricingService(runtime.pricing_repository, runtime.catalog_repository)

    cart_router._service = DefaultCartService(runtime.cart_repository, runtime.catalog_repository, runtime.pricing_service)
    
    class DummyYooKassaClient:
        async def create_payment_intent(self, amount, idempotence_key: str, description: str):
            return {"id": "dummy", "status": "pending"}

    orders_router._service = DefaultOrdersService(runtime.orders_repository, runtime.cart_repository, DummyYooKassaClient(), runtime.catalog_repository)
    admin_router._catalog_service = DefaultCatalogService(runtime.catalog_repository)

    async def _fake_user():
        return UserProfile(
            id=1,
            email="admin@example.com",
            full_name="Admin",
            phone=None,
            role=UserRole.ADMIN,
            hashed_password="x",
            created_at=datetime.utcnow(),
        )

    app.dependency_overrides[get_current_user] = _fake_user
    client = TestClient(app)

    category = client.post("/api/v1/admin/categories", json={"name": "Shoes"})
    assert category.status_code == 201
    category_id = category.json()["id"]

    product = client.post(
        "/api/v1/admin/products",
        json={"name": "Runner", "category_id": category_id},
    )
    assert product.status_code == 201
    product_id = product.json()["id"]

    sku = client.post("/api/v1/admin/skus", json={"product_id": product_id, "sku": "RUN-42", "attributes": {}})
    assert sku.status_code == 201
    variant_id = sku.json()["id"]

    inventory = client.post("/api/v1/admin/inventory", json={"sku_id": variant_id, "stock": 5})
    assert inventory.status_code == 201

    catalog_products = client.get("/api/v1/catalog/products")
    assert any(item["id"] == product_id for item in catalog_products.json())

    cart = client.post("/api/v1/cart/", json={"user_id": 42})
    cart_id = cart.json()["id"]

    upsert = client.put(f"/api/v1/cart/{cart_id}/items/{variant_id}", json={"variant_id": variant_id, "qty": 2, "promo_code": None})
    assert upsert.status_code == 200

    order = client.post("/api/v1/orders/checkout", json={"cart_id": cart_id, "payment_method": "cod"})
    assert order.status_code == 201
    order_id = order.json()["id"]
    stored = client.get(f"/api/v1/orders/{order_id}")
    assert stored.status_code == 200
    assert stored.json()["items"][0]["sku"] == "RUN-42"

    app.dependency_overrides.clear()