from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from app.db.commerce_models import CommerceAttribute, CommerceCategory, CommerceInventory, CommerceProduct, CommerceVariant
from app.db import sync_session
from app.modules.catalog.models.entity import Category, Inventory, Product, ProductAttribute, ProductVariant
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

    @staticmethod
    def _inventory(row: CommerceInventory) -> Inventory:
        return Inventory(id=row.id, variant_id=row.variant_id, qty=row.qty)

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
            if row is None:
                row = CommerceInventory(variant_id=variant_id, qty=qty)
                db.add(row)
            else:
                row.qty = qty
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