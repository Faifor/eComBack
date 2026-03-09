from abc import ABC, abstractmethod
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


class CatalogRepository(ABC):
    @abstractmethod
    def create_category(self, name: str, parent_id: int | None) -> Category: ...

    @abstractmethod
    def list_categories(self) -> list[Category]: ...

    @abstractmethod
    def get_category(self, category_id: int) -> Category | None: ...

    @abstractmethod
    def create_product(self, title: str, category_id: int, base_price: Decimal) -> Product: ...

    @abstractmethod
    def get_product(self, product_id: int) -> Product | None: ...

    @abstractmethod
    def list_products(self) -> list[Product]: ...

    @abstractmethod
    def create_variant(self, product_id: int, sku: str, title: str, base_price: Decimal | None) -> ProductVariant: ...

    @abstractmethod
    def get_variant(self, variant_id: int) -> ProductVariant | None: ...

    @abstractmethod
    def get_variant_by_sku(self, sku: str) -> ProductVariant | None: ...

    @abstractmethod
    def set_inventory(self, variant_id: int, qty: int) -> Inventory: ...

    @abstractmethod
    def get_inventory(self, variant_id: int) -> Inventory | None: ...

    @abstractmethod
    def add_inventory_movement(
        self,
        sku_id: int,
        movement_type: InventoryMovementType,
        qty: int,
        reason: str | None = None,
        source_type: str | None = None,
        source_id: str | None = None,
    ) -> InventoryMovement: ...

    @abstractmethod
    def list_inventory_movements(
        self,
        sku_id: int,
        created_from=None,
        created_to=None,
    ) -> list[InventoryMovement]: ...

    @abstractmethod
    def inventory_summary(self, sku_id: int) -> tuple[int, int, int]: ...


    @abstractmethod
    def add_attribute(self, product_id: int, name: str, value: str) -> ProductAttribute: ...

    @abstractmethod
    def list_attributes(self, product_id: int) -> list[ProductAttribute]: ...

    @abstractmethod
    def add_product_image(
        self,
        product_id: int,
        image_url: str,
        is_primary: bool = False,
        sort_order: int = 0,
    ) -> ProductImage: ...

    @abstractmethod
    def list_product_images(self, product_id: int) -> list[ProductImage]: ...

    @abstractmethod
    def add_product_review(self, product_id: int, user_id: int, rating: int, review: str) -> ProductReview: ...

    @abstractmethod
    def list_product_reviews(self, product_id: int) -> list[ProductReview]: ...

    @abstractmethod
    def get_product_rating_summary(self, product_id: int) -> ProductRatingSummary: ...
