from abc import ABC, abstractmethod
from decimal import Decimal

from app.modules.catalog.models.entity import Category, Inventory, Product, ProductAttribute, ProductVariant


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
    def add_attribute(self, product_id: int, name: str, value: str) -> ProductAttribute: ...

    @abstractmethod
    def list_attributes(self, product_id: int) -> list[ProductAttribute]: ...