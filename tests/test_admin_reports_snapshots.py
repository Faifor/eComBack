from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import sync_session
from app.db.base import Base
from app.db.commerce_models import CommerceCategory, CommerceOrder, CommerceOrderItem, CommerceProduct, CommerceVariant
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models.entity import User, UserRole
from app.modules.auth.repositories.user_repository import UserProfile

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots" / "admin_reports"


def _assert_snapshot(name: str, payload: object) -> None:
    expected = json.loads((SNAPSHOTS_DIR / f"{name}.json").read_text())
    assert payload == expected


def test_admin_reports_snapshots(tmp_path: Path) -> None:
    db_file = tmp_path / "reports.db"
    engine = create_engine(f"sqlite:///{db_file}", future=True)
    sync_session.sync_engine = engine
    sync_session.SyncSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with sync_session.SyncSessionLocal() as db:
        db.add_all(
            [
                User(id=1, email_enc="u1", email_hash="h1", full_name_enc="User 1", phone_enc=None, hashed_password="x", role=UserRole.USER),
                User(id=2, email_enc="u2", email_hash="h2", full_name_enc="User 2", phone_enc=None, hashed_password="x", role=UserRole.USER),
                User(id=3, email_enc="u3", email_hash="h3", full_name_enc="User 3", phone_enc=None, hashed_password="x", role=UserRole.USER),
            ]
        )

        cat1 = CommerceCategory(id=1, name="Shoes", parent_id=None)
        cat2 = CommerceCategory(id=2, name="T-Shirts", parent_id=None)
        product1 = CommerceProduct(id=1, title="Runner", category_id=1, base_price=Decimal("100.00"), is_active=True)
        product2 = CommerceProduct(id=2, title="Cotton Tee", category_id=2, base_price=Decimal("50.00"), is_active=True)
        v1 = CommerceVariant(id=1, product_id=1, sku="RUN-42", title="Runner 42", base_price=Decimal("100.00"))
        v2 = CommerceVariant(id=2, product_id=2, sku="TEE-M", title="Tee M", base_price=Decimal("50.00"))
        db.add_all([cat1, cat2, product1, product2, v1, v2])

        db.add_all(
            [
                CommerceOrder(
                    id=1,
                    user_id=1,
                    status="paid",
                    payment_method="card",
                    payment_id="p1",
                    payment_status="succeeded",
                    sales_channel="web",
                    promo_code="SPRING",
                    created_at=datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc),
                    total_price=Decimal("250.00"),
                ),
                CommerceOrder(
                    id=2,
                    user_id=1,
                    status="completed",
                    payment_method="card",
                    payment_id="p2",
                    payment_status="paid",
                    sales_channel="app",
                    promo_code=None,
                    created_at=datetime(2026, 3, 2, 12, 0, tzinfo=timezone.utc),
                    total_price=Decimal("100.00"),
                ),
                CommerceOrder(
                    id=3,
                    user_id=2,
                    status="pending",
                    payment_method="card",
                    payment_id="p3",
                    payment_status="pending",
                    sales_channel="web",
                    promo_code="SPRING",
                    created_at=datetime(2026, 3, 3, 12, 0, tzinfo=timezone.utc),
                    total_price=Decimal("60.00"),
                ),
            ]
        )

        db.add_all(
            [
                CommerceOrderItem(id=1, order_id=1, sku="RUN-42", title="Runner", qty=2, unit_price=Decimal("100.00"), line_total=Decimal("200.00"), rule_trace=[]),
                CommerceOrderItem(id=2, order_id=1, sku="TEE-M", title="Cotton Tee", qty=1, unit_price=Decimal("50.00"), line_total=Decimal("50.00"), rule_trace=[]),
                CommerceOrderItem(id=3, order_id=2, sku="RUN-42", title="Runner", qty=1, unit_price=Decimal("100.00"), line_total=Decimal("100.00"), rule_trace=[]),
                CommerceOrderItem(id=4, order_id=3, sku="TEE-M", title="Cotton Tee", qty=1, unit_price=Decimal("60.00"), line_total=Decimal("60.00"), rule_trace=[]),
            ]
        )
        db.commit()

    async def _fake_user() -> UserProfile:
        return UserProfile(
            id=1,
            email="admin@example.com",
            full_name="Admin",
            phone=None,
            role=UserRole.ADMIN,
            hashed_password="x",
            created_at=datetime.now(timezone.utc),
        )

    app.dependency_overrides[get_current_user] = _fake_user
    client = TestClient(app)

    _assert_snapshot("business_rules", client.get("/api/v1/admin/reports/business-rules").json())
    _assert_snapshot("revenue_month", client.get("/api/v1/admin/reports/revenue", params={"group_by": "month"}).json())
    _assert_snapshot("top_products_filtered", client.get("/api/v1/admin/reports/top-products", params={"category_id": 1, "channel": "web", "promo_code": "SPRING"}).json())
    _assert_snapshot("conversion_range", client.get("/api/v1/admin/reports/conversion", params={"from_dt": "2026-03-01T00:00:00Z", "to_dt": "2026-03-03T00:00:00Z"}).json())
    _assert_snapshot("average_check", client.get("/api/v1/admin/reports/average-check").json())
    _assert_snapshot("retention_ltv", client.get("/api/v1/admin/reports/retention-ltv").json())

    app.dependency_overrides.clear()