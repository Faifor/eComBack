from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from sqlalchemy import and_, select

from app.db.commerce_models import (
    CommerceAttribute,
    CommerceCategory,
    CommerceInventory,
    CommerceInventoryMovement,
    CommerceProduct,
    CommerceVariant,
)
from app.db import sync_session
from app.modules.catalog.models.entity import Category, Inventory, InventoryMovement, InventoryMovementType, Product, ProductAttribute, ProductVariant
from app.modules.catalog.repositories.base import CatalogRepository


class SQLAlchemyCatalogRepository(CatalogRepository):
    @staticmethod
    def _category(row: CommerceCategory) -> Category:
        return Category(id=row.id, name=row.name, parent_id=row.parent_id)

    @staticmethod
    def _product(row: CommerceProduct) -> Product:
        return Product(id=row.id, title=row.title, category_id=row.category_id, base_price=row.base_price, is_active=row.is_active)

    @staticmethod
    def _variant(row: CommerceVariant) -> ProductVariant:
        return ProductVariant(id=row.id, product_id=row.product_id, sku=row.sku, title=row.title, base_price=row.base_price)

    def _inventory(self, row: CommerceInventory) -> Inventory:
        on_hand, reserved, available = self.inventory_summary(row.variant_id)
        return Inventory(id=row.id, variant_id=row.variant_id, qty=row.qty, on_hand=on_hand, reserved=reserved, available=available)

    @staticmethod
    def _movement(row: CommerceInventoryMovement) -> InventoryMovement:
        return InventoryMovement(
            id=row.id,
            sku_id=row.sku_id,
            movement_type=InventoryMovementType(row.movement_type),
            qty=row.qty,
            reason=row.reason,
            source_type=row.source_type,
            source_id=row.source_id,
            created_at=row.created_at,
        )

    def create_category(self, name: str, parent_id: int | None) -> Category:
        with sync_session.SyncSessionLocal() as db:
            row = CommerceCategory(name=name, parent_id=parent_id)
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._category(row)

    def list_categories(self) -> list[Category]:
        with sync_session.SyncSessionLocal() as db:
            return [self._category(r) for r in db.scalars(select(CommerceCategory)).all()]

    def get_category(self, category_id: int) -> Category | None:
        with sync_session.SyncSessionLocal() as db:
            row = db.get(CommerceCategory, category_id)
            return self._category(row) if row else None

    def create_product(self, title: str, category_id: int, base_price: Decimal) -> Product:
        with sync_session.SyncSessionLocal() as db:
            row = CommerceProduct(title=title, category_id=category_id, base_price=base_price)
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._product(row)

    def get_product(self, product_id: int) -> Product | None:
        with sync_session.SyncSessionLocal() as db:
            row = db.get(CommerceProduct, product_id)
            return self._product(row) if row else None

    def list_products(self) -> list[Product]:
        with sync_session.SyncSessionLocal() as db:
            return [self._product(r) for r in db.scalars(select(CommerceProduct)).all()]

    def create_variant(self, product_id: int, sku: str, title: str, base_price: Decimal | None) -> ProductVariant:
        with sync_session.SyncSessionLocal() as db:
            row = CommerceVariant(product_id=product_id, sku=sku, title=title, base_price=base_price)
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._variant(row)

    def get_variant(self, variant_id: int) -> ProductVariant | None:
        with sync_session.SyncSessionLocal() as db:
            row = db.get(CommerceVariant, variant_id)
            return self._variant(row) if row else None

    def get_variant_by_sku(self, sku: str) -> ProductVariant | None:
        with sync_session.SyncSessionLocal() as db:
            row = db.scalar(select(CommerceVariant).where(CommerceVariant.sku == sku))
            return self._variant(row) if row else None

    def set_inventory(self, variant_id: int, qty: int) -> Inventory:
        with sync_session.SyncSessionLocal() as db:
            row = db.scalar(select(CommerceInventory).where(CommerceInventory.variant_id == variant_id))
            previous_qty = row.qty if row is not None else 0
            if row is None:
                row = CommerceInventory(variant_id=variant_id, qty=qty)
                db.add(row)
            else:
                row.qty = qty
                delta = qty - previous_qty
            if delta != 0:
                db.add(
                    CommerceInventoryMovement(
                        sku_id=variant_id,
                        movement_type=(InventoryMovementType.receipt if delta > 0 else InventoryMovementType.adjustment).value,
                        qty=delta,
                        reason="inventory_sync",
                        source_type="inventory",
                        source_id=str(variant_id),
                    )
                )
            db.commit()
            db.refresh(row)
            return self._inventory(row)

    def get_inventory(self, variant_id: int) -> Inventory | None:
        with sync_session.SyncSessionLocal() as db:
            row = db.scalar(select(CommerceInventory).where(CommerceInventory.variant_id == variant_id))
            return self._inventory(row) if row else None

    def add_attribute(self, product_id: int, name: str, value: str) -> ProductAttribute:
        with sync_session.SyncSessionLocal() as db:
            row = CommerceAttribute(product_id=product_id, name=name, value=value)
            db.add(row)
            db.commit()
            db.refresh(row)
            return ProductAttribute(id=row.id, product_id=row.product_id, name=row.name, value=row.value)

    def list_attributes(self, product_id: int) -> list[ProductAttribute]:
        with sync_session.SyncSessionLocal() as db:
            rows = db.scalars(select(CommerceAttribute).where(CommerceAttribute.product_id == product_id)).all()
            return [ProductAttribute(id=r.id, product_id=r.product_id, name=r.name, value=r.value) for r in rows]

    def add_inventory_movement(
        self,
        sku_id: int,
        movement_type: InventoryMovementType,
        qty: int,
        reason: str | None = None,
        source_type: str | None = None,
        source_id: str | None = None,
    ) -> InventoryMovement:
        with sync_session.SyncSessionLocal() as db:
            row = CommerceInventoryMovement(
                sku_id=sku_id,
                movement_type=movement_type.value,
                qty=qty,
                reason=reason,
                source_type=source_type,
                source_id=source_id,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._movement(row)

    def list_inventory_movements(
        self,
        sku_id: int,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> list[InventoryMovement]:
        with sync_session.SyncSessionLocal() as db:
            query = select(CommerceInventoryMovement).where(CommerceInventoryMovement.sku_id == sku_id)
            conditions = []
            if created_from is not None:
                conditions.append(CommerceInventoryMovement.created_at >= created_from)
            if created_to is not None:
                conditions.append(CommerceInventoryMovement.created_at <= created_to)
            if conditions:
                query = query.where(and_(*conditions))
            query = query.order_by(CommerceInventoryMovement.created_at.desc())
            rows = db.scalars(query).all()
            return [self._movement(row) for row in rows]

    def inventory_summary(self, sku_id: int) -> tuple[int, int, int]:
        movements = self.list_inventory_movements(sku_id)
        on_hand = 0
        reserved = 0
        for movement in movements:
            if movement.movement_type in {InventoryMovementType.receipt, InventoryMovementType.returned}:
                on_hand += movement.qty
            elif movement.movement_type == InventoryMovementType.sale:
                on_hand -= movement.qty
            elif movement.movement_type == InventoryMovementType.adjustment:
                on_hand += movement.qty
            elif movement.movement_type == InventoryMovementType.reserve:
                reserved += movement.qty
            elif movement.movement_type == InventoryMovementType.release:
                reserved -= movement.qty
        if reserved < 0:
            reserved = 0
        return on_hand, reserved, on_hand - reserved