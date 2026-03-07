from __future__ import annotations

from sqlalchemy import select

from app.db.commerce_models import CommercePricingRule
from app.db import sync_session
from app.modules.pricing.models.entity import PricingRule
from app.modules.pricing.repositories.base import PricingRepository


class SQLAlchemyPricingRepository(PricingRepository):
    @staticmethod
    def _map(row: CommercePricingRule) -> PricingRule:
        return PricingRule(
            id=row.id,
            name=row.name,
            priority=row.priority,
            rule_type=row.rule_type,
            value=row.value,
            product_id=row.product_id,
            variant_id=row.variant_id,
            min_qty=row.min_qty,
            coupon_code=row.coupon_code,
            active=row.active,
        )

    def create_rule(self, rule: PricingRule) -> PricingRule:
        with sync_session.SyncSessionLocal() as db:
            row = CommercePricingRule(**rule.__dict__)
            row.id = None
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._map(row)

    def list_rules(self) -> list[PricingRule]:
        with sync_session.SyncSessionLocal() as db:
            return [self._map(r) for r in db.scalars(select(CommercePricingRule)).all()]