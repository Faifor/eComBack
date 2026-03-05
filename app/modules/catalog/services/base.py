from abc import ABC, abstractmethod
from app.modules.catalog.schemas.dto import (
    CategoryCreate,
    CategoryRead,
    InventoryRead,
    InventorySet,
    ProductAttributeCreate,
    ProductAttributeRead,
    ProductCreate,
    ProductRead,
    ProductVariantCreate,
    ProductVariantRead,
)


class CatalogService(ABC):
    @abstractmethod
    def create_category(self, payload: CategoryCreate) -> CategoryRead: ...

    @abstractmethod
    def list_categories(self) -> list[CategoryRead]: ...

    @abstractmethod
    def create_product(self, payload: ProductCreate) -> ProductRead: ...

    @abstractmethod
    def list_products(self) -> list[ProductRead]: ...

    @abstractmethod
    def create_variant(self, payload: ProductVariantCreate) -> ProductVariantRead: ...

    @abstractmethod
    def set_inventory(self, payload: InventorySet) -> InventoryRead: ...

    @abstractmethod
    def add_attribute(self, payload: ProductAttributeCreate) -> ProductAttributeRead: ...