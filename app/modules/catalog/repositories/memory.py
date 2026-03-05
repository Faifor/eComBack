from decimal import Decimal

from app.modules.catalog.models.entity import Category, Inventory, Product, ProductAttribute, ProductVariant
from app.modules.catalog.repositories.base import CatalogRepository


class InMemoryCatalogRepository(CatalogRepository):
    def __init__(self) -> None:
        self._next_ids = {"category": 1, "product": 1, "variant": 1, "inventory": 1, "attribute": 1}
        self._categories: dict[int, Category] = {}
        self._products: dict[int, Product] = {}
        self._variants: dict[int, ProductVariant] = {}
        self._inventory: dict[int, Inventory] = {}
        self._attributes: dict[int, ProductAttribute] = {}

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
    
    def create_product(self, title: str, category_id: int, base_price: Decimal) -> Product:
        item = Product(id=self._next_id("product"), title=title, category_id=category_id, base_price=base_price)
        self._products[item.id] = item
        return item

    def get_product(self, product_id: int) -> Product | None:
        return self._products.get(product_id)

    def list_products(self) -> list[Product]:
        return list(self._products.values())

    def create_variant(self, product_id: int, sku: str, title: str, base_price: Decimal | None) -> ProductVariant:
        item = ProductVariant(id=self._next_id("variant"), product_id=product_id, sku=sku, title=title, base_price=base_price)
        self._variants[item.id] = item
        return item

    def get_variant(self, variant_id: int) -> ProductVariant | None:
        return self._variants.get(variant_id)

    def get_variant_by_sku(self, sku: str) -> ProductVariant | None:
        return next((v for v in self._variants.values() if v.sku == sku), None)

    def set_inventory(self, variant_id: int, qty: int) -> Inventory:
        existing = self._inventory.get(variant_id)
        if existing:
            existing.qty = qty
            return existing
        item = Inventory(id=self._next_id("inventory"), variant_id=variant_id, qty=qty)
        self._inventory[variant_id] = item
        return item

    def get_inventory(self, variant_id: int) -> Inventory | None:
        return self._inventory.get(variant_id)

    def add_attribute(self, product_id: int, name: str, value: str) -> ProductAttribute:
        item = ProductAttribute(id=self._next_id("attribute"), product_id=product_id, name=name, value=value)
        self._attributes[item.id] = item
        return item

    def list_attributes(self, product_id: int) -> list[ProductAttribute]:
        return [attr for attr in self._attributes.values() if attr.product_id == product_id]