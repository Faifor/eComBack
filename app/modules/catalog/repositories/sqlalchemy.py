from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from sqlalchemy import and_, delete, select

from app.db.commerce_models import (
    CommerceAttribute,
    CommerceCategory,
    CommerceInventory,
    CommerceInventoryMovement,
    CommerceProduct,
    CommerceProductImage,
    CommerceProductReview,
    CommercePricingRule,
    CommerceVariant,
)
from app.db import sync_session
from app.modules.catalog.models.entity import (
    Category,
    Inventory,
    InventoryMovement,
    InventoryMovementType,
    Product,
    ProductAttribute,
    ProductImage,
    ProductRatingSummary,
    ProductReview,
    ProductVariant,
)
from app.modules.catalog.repositories.base import CatalogRepository


class SQLAlchemyCatalogRepository(CatalogRepository):
    @staticmethod
    def _category(row: CommerceCategory) -> Category:
        return Category(id=row.id, name=row.name, parent_id=row.parent_id)

    @staticmethod
    def _product(row: CommerceProduct) -> Product:
        return Product(id=row.id, title=row.title, category_id=row.category_id, base_price=row.base_price, is_active=row.is_active, description=row.description)

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

    def delete_category(self, category_id: int) -> None:
        with sync_session.SyncSessionLocal() as db:
            category = db.get(CommerceCategory, category_id)
            if category is None:
                raise ValueError("category not found")

            has_products = db.scalar(select(CommerceProduct.id).where(CommerceProduct.category_id == category_id).limit(1))
            if has_products is not None:
                raise ValueError("category has products")

            db.delete(category)
            db.commit()

    def create_product(self, title: str, category_id: int, base_price: Decimal, description: str | None = None) -> Product:
        with sync_session.SyncSessionLocal() as db:
            row = CommerceProduct(title=title, category_id=category_id, base_price=base_price, description=description)
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

    def delete_product(self, product_id: int) -> None:
        with sync_session.SyncSessionLocal() as db:
            product = db.get(CommerceProduct, product_id)
            if product is None:
                raise ValueError("product not found")

            variant_ids = db.scalars(select(CommerceVariant.id).where(CommerceVariant.product_id == product_id)).all()

            db.execute(delete(CommerceProductImage).where(CommerceProductImage.product_id == product_id))
            db.execute(delete(CommerceProductReview).where(CommerceProductReview.product_id == product_id))
            db.execute(delete(CommerceAttribute).where(CommerceAttribute.product_id == product_id))
            db.execute(delete(CommercePricingRule).where(CommercePricingRule.product_id == product_id))

            if variant_ids:
                db.execute(delete(CommercePricingRule).where(CommercePricingRule.variant_id.in_(variant_ids)))
                db.execute(delete(CommerceInventoryMovement).where(CommerceInventoryMovement.sku_id.in_(variant_ids)))
                db.execute(delete(CommerceInventory).where(CommerceInventory.variant_id.in_(variant_ids)))
                db.execute(delete(CommerceVariant).where(CommerceVariant.id.in_(variant_ids)))

            db.delete(product)
            db.commit()

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


    def list_variants_by_product(self, product_id: int) -> list[ProductVariant]:
        with sync_session.SyncSessionLocal() as db:
            rows = db.scalars(select(CommerceVariant).where(CommerceVariant.product_id == product_id)).all()
            return [self._variant(row) for row in rows]

    def set_inventory(self, variant_id: int, qty: int) -> Inventory:
        with sync_session.SyncSessionLocal() as db:
            row = db.scalar(select(CommerceInventory).where(CommerceInventory.variant_id == variant_id))
            previous_qty = row.qty if row is not None else 0
            delta = qty - previous_qty
            if row is None:
                row = CommerceInventory(variant_id=variant_id, qty=qty)
                db.add(row)
            else:
                row.qty = qty
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

    def add_attribute(self, product_id: int, name: str, value: str, variant_id: int | None = None) -> ProductAttribute:
        with sync_session.SyncSessionLocal() as db:
            row = CommerceAttribute(product_id=product_id, variant_id=variant_id, name=name, value=value)
            db.add(row)
            db.commit()
            db.refresh(row)
            return ProductAttribute(id=row.id, product_id=row.product_id, variant_id=row.variant_id, name=row.name, value=row.value)

    def list_attributes(self, product_id: int) -> list[ProductAttribute]:
        with sync_session.SyncSessionLocal() as db:
            rows = db.scalars(select(CommerceAttribute).where(CommerceAttribute.product_id == product_id)).all()
            return [
                ProductAttribute(id=r.id, product_id=r.product_id, variant_id=r.variant_id, name=r.name, value=r.value)
                for r in rows
            ]

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

    def add_product_image(
        self,
        product_id: int,
        image_url: str,
        is_primary: bool = False,
        sort_order: int = 0,
    ) -> ProductImage:
        with sync_session.SyncSessionLocal() as db:
            row = CommerceProductImage(
                product_id=product_id,
                image_url=image_url,
                is_primary=is_primary,
                sort_order=sort_order,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return ProductImage(
                id=row.id,
                product_id=row.product_id,
                image_url=row.image_url,
                is_primary=row.is_primary,
                sort_order=row.sort_order,
                created_at=row.created_at,
            )

    def list_product_images(self, product_id: int) -> list[ProductImage]:
        with sync_session.SyncSessionLocal() as db:
            rows = db.scalars(
                select(CommerceProductImage)
                .where(CommerceProductImage.product_id == product_id)
                .order_by(CommerceProductImage.sort_order.asc(), CommerceProductImage.id.asc())
            ).all()
            return [
                ProductImage(
                    id=row.id,
                    product_id=row.product_id,
                    image_url=row.image_url,
                    is_primary=row.is_primary,
                    sort_order=row.sort_order,
                    created_at=row.created_at,
                )
                for row in rows
            ]

    def add_product_review(self, product_id: int, user_id: int, rating: int, review: str) -> ProductReview:
        with sync_session.SyncSessionLocal() as db:
            row = CommerceProductReview(product_id=product_id, user_id=user_id, rating=rating, review=review)
            db.add(row)
            db.commit()
            db.refresh(row)
            return ProductReview(
                id=row.id,
                product_id=row.product_id,
                user_id=row.user_id,
                rating=row.rating,
                review=row.review,
                created_at=row.created_at,
            )

    def list_product_reviews(self, product_id: int) -> list[ProductReview]:
        with sync_session.SyncSessionLocal() as db:
            rows = db.scalars(
                select(CommerceProductReview)
                .where(CommerceProductReview.product_id == product_id)
                .order_by(CommerceProductReview.created_at.desc())
            ).all()
            return [
                ProductReview(
                    id=row.id,
                    product_id=row.product_id,
                    user_id=row.user_id,
                    rating=row.rating,
                    review=row.review,
                    created_at=row.created_at,
                )
                for row in rows
            ]

    def get_product_rating_summary(self, product_id: int) -> ProductRatingSummary:
        reviews = self.list_product_reviews(product_id)
        if not reviews:
            return ProductRatingSummary(average_rating=0.0, reviews_count=0)
        return ProductRatingSummary(
            average_rating=round(sum(item.rating for item in reviews) / len(reviews), 2),
            reviews_count=len(reviews),
        )
