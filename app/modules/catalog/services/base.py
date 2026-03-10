from abc import ABC, abstractmethod
from app.modules.catalog.schemas.dto import (
    CategoryCreate,
    CategoryRead,
    InventoryRead,
    InventorySet,
    ProductAttributeCreate,
    ProductAttributeRead,
    ProductImageRead,
    ProductCreate,
    ProductDetailsRead,
    ProductRead,
    ProductReviewCreate,
    ProductReviewRead,
    ProductVariantCreate,
    ProductVariantRead,
)


class CatalogService(ABC):
    @abstractmethod
    def create_category(self, payload: CategoryCreate) -> CategoryRead: ...

    @abstractmethod
    def list_categories(self) -> list[CategoryRead]: ...

    @abstractmethod
    def delete_category(self, category_id: int) -> None: ...

    @abstractmethod
    def create_product(self, payload: ProductCreate) -> ProductRead: ...

    @abstractmethod
    def list_products(
        self,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        q: str | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> list[ProductRead]: ...

    @abstractmethod
    def delete_product(self, product_id: int) -> None: ...

    @abstractmethod
    def create_variant(self, payload: ProductVariantCreate) -> ProductVariantRead: ...

    @abstractmethod
    def set_inventory(self, payload: InventorySet) -> InventoryRead: ...

    @abstractmethod
    def get_inventory(self, variant_id: int) -> InventoryRead | None: ...

    @abstractmethod
    def add_attribute(self, payload: ProductAttributeCreate) -> ProductAttributeRead: ...

    @abstractmethod
    def add_product_image(self, product_id: int, image_url: str, is_primary: bool = False, sort_order: int = 0) -> ProductImageRead: ...

    @abstractmethod
    def add_review(self, product_id: int, payload: ProductReviewCreate) -> ProductReviewRead: ...

    @abstractmethod
    def list_reviews(self, product_id: int) -> list[ProductReviewRead]: ...

    @abstractmethod
    def get_product_details(self, product_id: int) -> ProductDetailsRead: ...
