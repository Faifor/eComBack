from datetime import datetime, timezone
from decimal import Decimal

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


class InMemoryCatalogRepository(CatalogRepository):
    def __init__(self) -> None:
        self._next_ids = {
            "category": 1,
            "product": 1,
            "variant": 1,
            "inventory": 1,
            "attribute": 1,
            "movement": 1,
            "image": 1,
            "review": 1,
        }
        self._categories: dict[int, Category] = {}
        self._products: dict[int, Product] = {}
        self._variants: dict[int, ProductVariant] = {}
        self._inventory: dict[int, Inventory] = {}
        self._attributes: dict[int, ProductAttribute] = {}
        self._images: dict[int, ProductImage] = {}
        self._reviews: dict[int, ProductReview] = {}
        self._movements: list[InventoryMovement] = []

    def _next_id(self, key: str) -> int:
        val = self._next_ids[key]
        self._next_ids[key] += 1
        return val

    def create_category(self, name: str, parent_id: int | None) -> Category:
        item = Category(id=self._next_id("category"), name=name, parent_id=parent_id)
        self._categories[item.id] = item
        return item

    def list_categories(self) -> list[Category]:
        return list(self._categories.values())

    def get_category(self, category_id: int) -> Category | None:
        return self._categories.get(category_id)

    def delete_category(self, category_id: int) -> None:
        if category_id not in self._categories:
            raise ValueError("category not found")
        if any(product.category_id == category_id for product in self._products.values()):
            raise ValueError("category has products")
        del self._categories[category_id]
    
    def create_product(self, title: str, category_id: int, base_price: Decimal, description: str | None = None) -> Product:
        item = Product(id=self._next_id("product"), title=title, category_id=category_id, base_price=base_price, description=description)
        self._products[item.id] = item
        return item

    def get_product(self, product_id: int) -> Product | None:
        return self._products.get(product_id)

    def list_products(self) -> list[Product]:
        return list(self._products.values())

    def delete_product(self, product_id: int) -> None:
        if product_id not in self._products:
            raise ValueError("product not found")
        del self._products[product_id]

        variant_ids = [variant.id for variant in self._variants.values() if variant.product_id == product_id]
        self._variants = {variant_id: variant for variant_id, variant in self._variants.items() if variant.product_id != product_id}
        self._inventory = {variant_id: inventory for variant_id, inventory in self._inventory.items() if variant_id not in variant_ids}
        self._movements = [movement for movement in self._movements if movement.sku_id not in variant_ids]
        self._attributes = {
            attribute_id: attribute
            for attribute_id, attribute in self._attributes.items()
            if attribute.product_id != product_id
        }
        self._images = {
            image_id: image
            for image_id, image in self._images.items()
            if image.product_id != product_id
        }
        self._reviews = {
            review_id: review
            for review_id, review in self._reviews.items()
            if review.product_id != product_id
        }

    def create_variant(self, product_id: int, sku: str, title: str, base_price: Decimal | None) -> ProductVariant:
        item = ProductVariant(id=self._next_id("variant"), product_id=product_id, sku=sku, title=title, base_price=base_price)
        self._variants[item.id] = item
        return item

    def get_variant(self, variant_id: int) -> ProductVariant | None:
        return self._variants.get(variant_id)

    def get_variant_by_sku(self, sku: str) -> ProductVariant | None:
        return next((v for v in self._variants.values() if v.sku == sku), None)


    def list_variants_by_product(self, product_id: int) -> list[ProductVariant]:
        return [variant for variant in self._variants.values() if variant.product_id == product_id]

    def set_inventory(self, variant_id: int, qty: int) -> Inventory:
        existing = self._inventory.get(variant_id)
        previous_qty = existing.qty if existing else 0
        if existing:
            existing.qty = qty
        else:
            existing = Inventory(id=self._next_id("inventory"), variant_id=variant_id, qty=qty)
            self._inventory[variant_id] = existing
        delta = qty - previous_qty
        if delta != 0:
            movement_type = InventoryMovementType.receipt if delta > 0 else InventoryMovementType.adjustment
            self.add_inventory_movement(variant_id, movement_type, delta, reason="inventory_sync", source_type="inventory", source_id=str(variant_id))
        return self.get_inventory(variant_id)

    def get_inventory(self, variant_id: int) -> Inventory | None:
        raw = self._inventory.get(variant_id)
        if raw is None:
            return None
        on_hand, reserved, available = self.inventory_summary(variant_id)
        return Inventory(id=raw.id, variant_id=raw.variant_id, qty=raw.qty, on_hand=on_hand, reserved=reserved, available=available)

    def add_attribute(self, product_id: int, name: str, value: str, variant_id: int | None = None) -> ProductAttribute:
        item = ProductAttribute(
            id=self._next_id("attribute"),
            product_id=product_id,
            variant_id=variant_id,
            name=name,
            value=value,
        )
        self._attributes[item.id] = item
        return item

    def list_attributes(self, product_id: int) -> list[ProductAttribute]:
        return [attr for attr in self._attributes.values() if attr.product_id == product_id]

    def add_inventory_movement(
        self,
        sku_id: int,
        movement_type: InventoryMovementType,
        qty: int,
        reason: str | None = None,
        source_type: str | None = None,
        source_id: str | None = None,
    ) -> InventoryMovement:
        movement = InventoryMovement(
            id=self._next_id("movement"),
            sku_id=sku_id,
            movement_type=movement_type,
            qty=qty,
            reason=reason,
            source_type=source_type,
            source_id=source_id,
            created_at=datetime.now(timezone.utc),
        )
        self._movements.append(movement)
        return movement

    def list_inventory_movements(self, sku_id: int, created_from=None, created_to=None) -> list[InventoryMovement]:
        rows = [m for m in self._movements if m.sku_id == sku_id]
        if created_from is not None:
            rows = [m for m in rows if m.created_at >= created_from]
        if created_to is not None:
            rows = [m for m in rows if m.created_at <= created_to]
        return sorted(rows, key=lambda m: m.created_at, reverse=True)

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
        available = on_hand - reserved
        return on_hand, reserved, available

    def add_product_image(
        self,
        product_id: int,
        image_url: str,
        is_primary: bool = False,
        sort_order: int = 0,
    ) -> ProductImage:
        item = ProductImage(
            id=self._next_id("image"),
            product_id=product_id,
            image_url=image_url,
            is_primary=is_primary,
            sort_order=sort_order,
            created_at=datetime.now(timezone.utc),
        )
        self._images[item.id] = item
        return item

    def list_product_images(self, product_id: int) -> list[ProductImage]:
        return sorted(
            [image for image in self._images.values() if image.product_id == product_id],
            key=lambda image: (image.sort_order, image.id),
        )

    def add_product_review(self, product_id: int, user_id: int, rating: int, review: str) -> ProductReview:
        item = ProductReview(
            id=self._next_id("review"),
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            review=review,
            created_at=datetime.now(timezone.utc),
        )
        self._reviews[item.id] = item
        return item

    def list_product_reviews(self, product_id: int) -> list[ProductReview]:
        return sorted(
            [review for review in self._reviews.values() if review.product_id == product_id],
            key=lambda review: review.created_at,
            reverse=True,
        )

    def get_product_rating_summary(self, product_id: int) -> ProductRatingSummary:
        reviews = self.list_product_reviews(product_id)
        if not reviews:
            return ProductRatingSummary(average_rating=0.0, reviews_count=0)
        return ProductRatingSummary(
            average_rating=round(sum(item.rating for item in reviews) / len(reviews), 2),
            reviews_count=len(reviews),
        )
