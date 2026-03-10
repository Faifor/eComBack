from __future__ import annotations

from datetime import datetime
import io
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db import sync_session
from app.db.commerce_models import CommerceAttribute, CommerceInventory, CommerceProductImage, CommerceProductReview, CommerceVariant
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

    image_upload = client.post(
        f"/api/v1/admin/products/{product_id}/images",
        files=[("files", ("runner.jpg", io.BytesIO(b"fake-image"), "image/jpeg"))],
    )
    assert image_upload.status_code == 201
    assert image_upload.json()[0]["product_id"] == product_id

    review = client.post(
        f"/api/v1/catalog/products/{product_id}/reviews",
        json={"user_id": 42, "rating": 5, "review": "Отличные кроссовки"},
    )
    assert review.status_code == 201

    catalog_products = client.get("/api/v1/catalog/products")
    product_payload = next(item for item in catalog_products.json() if item["id"] == product_id)
    assert product_payload["images"]
    assert product_payload["average_rating"] == 5.0
    assert product_payload["reviews_count"] == 1

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

def test_admin_import_modes_bulk_and_idempotency(tmp_path: Path) -> None:
    db_file = tmp_path / "integration_imports.db"
    engine = create_engine(f"sqlite:///{db_file}", future=True)
    sync_session.sync_engine = engine
    sync_session.SyncSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    runtime.catalog_repository = SQLAlchemyCatalogRepository()
    runtime.pricing_repository = SQLAlchemyPricingRepository()
    runtime.pricing_service = DefaultPricingService(runtime.pricing_repository, runtime.catalog_repository)
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

    payload = {
        "filename": "products.csv",
        "content": "sku,product_name,category_name,stock,external_key,version\nRUN-43,Runner,Footwear,7,ext-run,1",
    }

    dry = client.post("/api/v1/admin/imports/products", params={"dry_run": True, "upsert": True}, json=payload)
    assert dry.status_code == 200
    assert dry.json()["created"] == 1

    imported = client.post(
        "/api/v1/admin/imports/products",
        params={"dry_run": False, "upsert": True, "external_key": "batch-a", "version": "v1"},
        json=payload,
    )
    assert imported.status_code == 200
    assert imported.json()["created"] == 1

    duplicated = client.post(
        "/api/v1/admin/imports/products",
        params={"dry_run": False, "upsert": True, "external_key": "batch-a", "version": "v1"},
        json=payload,
    )
    assert duplicated.status_code == 200
    assert duplicated.json()["skipped"] == 1

    updated = client.post(
        "/api/v1/admin/imports/products",
        params={"dry_run": False, "upsert": True, "external_key": "batch-a", "version": "v2"},
        json={
            "filename": "products.csv",
            "content": "sku,product_name,category_name,stock,external_key,version\nRUN-43,Runner 2,Footwear,9,ext-run,2",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["updated"] == 1

    rollback = client.post(
        "/api/v1/admin/imports/products",
        params={"dry_run": False, "upsert": False, "rollback_on_error": True},
        json={
            "filename": "products.csv",
            "content": "sku,product_name,category_name,stock\nRUN-44,Runner,Footwear,5\nRUN-43,Runner,Footwear,5",
        },
    )
    assert rollback.status_code == 200
    assert rollback.json()["created"] == 0
    assert rollback.json()["errors"]

    price_bulk = client.post("/api/v1/admin/bulk/sku-prices", json=[{"sku": "RUN-43", "price": 199.99}])
    assert price_bulk.status_code == 200
    assert price_bulk.json()["updated"] == 1

    stock_bulk = client.post("/api/v1/admin/bulk/sku-stocks", json=[{"sku": "RUN-43", "stock": 3}])
    assert stock_bulk.status_code == 200
    assert stock_bulk.json()["updated"] == 1

    status_bulk = client.post("/api/v1/admin/bulk/sku-statuses", json=[{"sku": "RUN-43", "status": "inactive"}])
    assert status_bulk.status_code == 200
    assert status_bulk.json()["updated"] == 1

    app.dependency_overrides.clear()


def test_user_permissions_are_limited_to_storefront_actions(tmp_path: Path) -> None:
    db_file = tmp_path / "integration_permissions.db"
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

    orders_router._service = DefaultOrdersService(
        runtime.orders_repository, runtime.cart_repository, DummyYooKassaClient(), runtime.catalog_repository
    )
    admin_router._catalog_service = DefaultCatalogService(runtime.catalog_repository)

    async def _fake_user():
        return UserProfile(
            id=7,
            email="user@example.com",
            full_name="User",
            phone=None,
            role=UserRole.USER,
            hashed_password="x",
            created_at=datetime.utcnow(),
        )

    app.dependency_overrides[get_current_user] = _fake_user
    client = TestClient(app)

    admin_create = client.post("/api/v1/admin/categories", json={"name": "Forbidden"})
    assert admin_create.status_code == 403

    catalog_create = client.post("/api/v1/catalog/categories", json={"name": "Forbidden"})
    assert catalog_create.status_code == 403

    catalog_read = client.get("/api/v1/catalog/products")
    assert catalog_read.status_code == 200

    cart = client.post("/api/v1/cart/", json={"user_id": 7})
    assert cart.status_code == 201

    app.dependency_overrides.clear()


def test_admin_validations_and_product_details_endpoint(tmp_path: Path) -> None:
    db_file = tmp_path / "integration_validations.db"
    engine = create_engine(f"sqlite:///{db_file}", future=True)
    sync_session.sync_engine = engine
    sync_session.SyncSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    runtime.catalog_repository = SQLAlchemyCatalogRepository()
    runtime.pricing_repository = SQLAlchemyPricingRepository()
    runtime.pricing_service = DefaultPricingService(runtime.pricing_repository, runtime.catalog_repository)
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

    bad_category = client.post("/api/v1/admin/categories", json={"name": "   "})
    assert bad_category.status_code == 422

    category = client.post("/api/v1/admin/categories", json={"name": "Electronics"})
    category_id = category.json()["id"]

    bad_product_name = client.post("/api/v1/admin/products", json={"name": " ", "category_id": category_id})
    assert bad_product_name.status_code == 422

    bad_product_category = client.post("/api/v1/admin/products", json={"name": "Phone", "category_id": 0})
    assert bad_product_category.status_code == 422

    product = client.post(
        "/api/v1/admin/products",
        json={"name": "Phone", "category_id": category_id, "description": "Great phone", "base_price": "120000.00"},
    )
    assert product.status_code == 201
    product_id = product.json()["id"]

    update_description = client.put(
        f"/api/v1/admin/products/{product_id}/description",
        json={"description": "Updated description"},
    )
    assert update_description.status_code == 200
    assert update_description.json()["description"] == "Updated description"

    bad_sku = client.post("/api/v1/admin/skus", json={"product_id": 0, "sku": ""})
    assert bad_sku.status_code == 422

    sku = client.post("/api/v1/admin/skus", json={"product_id": product_id, "sku": "PHN-1"})
    assert sku.status_code == 201
    variant_id = sku.json()["id"]

    duplicate_sku = client.post("/api/v1/admin/skus", json={"product_id": product_id, "sku": "PHN-1"})
    assert duplicate_sku.status_code == 409
    assert duplicate_sku.json()["detail"] == "sku already exists"

    bad_inventory = client.post("/api/v1/admin/inventory", json={"sku_id": variant_id})
    assert bad_inventory.status_code == 422

    inventory = client.post("/api/v1/admin/inventory", json={"sku_id": variant_id, "stock": 3})
    assert inventory.status_code == 201

    bad_bulk_prices = client.post("/api/v1/admin/bulk/sku-prices", json=[{"sku": "", "price": 0}])
    assert bad_bulk_prices.status_code == 422

    client.post("/api/v1/catalog/attributes", json={"product_id": product_id, "name": "color", "value": "black"})
    client.post(f"/api/v1/catalog/products/{product_id}/reviews", json={"user_id": 99, "rating": 4, "review": "Good"})

    details = client.get(f"/api/v1/catalog/products/{product_id}")
    assert details.status_code == 200
    payload = details.json()
    assert payload["description"] == "Updated description"
    assert payload["reviews_count"] == 1
    assert payload["average_rating"] == 4.0
    assert payload["reviews"]
    assert payload["variants"]
    assert payload["attributes"]
    variants = client.get(f"/api/v1/catalog/products/{product_id}/variants")
    assert variants.status_code == 200
    assert len(variants.json()) == 1

    second_product = client.post(
        "/api/v1/admin/products",
        json={"name": "Budget Phone", "category_id": category_id, "base_price": "50000.00"},
    )
    assert second_product.status_code == 201

    filtered = client.get("/api/v1/catalog/products", params={"min_price": 100000, "sort_by": "base_price", "sort_order": "desc"})
    assert filtered.status_code == 200
    filtered_payload = filtered.json()
    assert len(filtered_payload) == 1
    assert filtered_payload[0]["title"] == "Phone"

    search = client.get("/api/v1/catalog/products", params={"q": "budget"})
    assert search.status_code == 200
    assert len(search.json()) == 1

    app.dependency_overrides.clear()


def test_admin_can_delete_category_and_product_with_rules(tmp_path: Path) -> None:
    db_file = tmp_path / "integration_delete.db"
    engine = create_engine(f"sqlite:///{db_file}", future=True)
    sync_session.sync_engine = engine
    sync_session.SyncSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    runtime.catalog_repository = SQLAlchemyCatalogRepository()
    runtime.pricing_repository = SQLAlchemyPricingRepository()
    runtime.pricing_service = DefaultPricingService(runtime.pricing_repository, runtime.catalog_repository)
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

    category = client.post("/api/v1/admin/categories", json={"name": "Delete me"})
    assert category.status_code == 201
    category_id = category.json()["id"]

    product = client.post("/api/v1/admin/products", json={"name": "Disposable", "category_id": category_id})
    assert product.status_code == 201
    product_id = product.json()["id"]

    variant = client.post("/api/v1/admin/skus", json={"product_id": product_id, "sku": "DEL-1"})
    assert variant.status_code == 201
    variant_id = variant.json()["id"]

    inventory = client.post("/api/v1/admin/inventory", json={"sku_id": variant_id, "stock": 4})
    assert inventory.status_code == 201

    image_upload = client.post(
        f"/api/v1/admin/products/{product_id}/images",
        files=[("files", ("test.jpg", io.BytesIO(b"x"), "image/jpeg"))],
    )
    assert image_upload.status_code == 201

    review = client.post(
        f"/api/v1/catalog/products/{product_id}/reviews",
        json={"user_id": 10, "rating": 5, "review": "great"},
    )
    assert review.status_code == 201

    category_delete_with_products = client.delete(f"/api/v1/admin/categories/{category_id}")
    assert category_delete_with_products.status_code == 409

    product_delete = client.delete(f"/api/v1/admin/products/{product_id}")
    assert product_delete.status_code == 204

    with sync_session.SyncSessionLocal() as db:
        assert db.scalar(select(CommerceVariant.id).where(CommerceVariant.product_id == product_id)) is None
        assert db.scalar(select(CommerceInventory.id).where(CommerceInventory.variant_id == variant_id)) is None
        assert db.scalar(select(CommerceAttribute.id).where(CommerceAttribute.product_id == product_id)) is None
        assert db.scalar(select(CommerceProductImage.id).where(CommerceProductImage.product_id == product_id)) is None
        assert db.scalar(select(CommerceProductReview.id).where(CommerceProductReview.product_id == product_id)) is None

    category_delete = client.delete(f"/api/v1/admin/categories/{category_id}")
    assert category_delete.status_code == 204

    product_delete_again = client.delete(f"/api/v1/admin/products/{product_id}")
    assert product_delete_again.status_code == 404

    app.dependency_overrides.clear()
