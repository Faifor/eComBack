from app.modules.catalog.repositories.base import CatalogRepository
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
from app.modules.catalog.services.base import CatalogService


class DefaultCatalogService(CatalogService):
    def __init__(self, repository: CatalogRepository) -> None:
        self._repository = repository

    def create_category(self, payload: CategoryCreate) -> CategoryRead:
        if payload.parent_id is not None and self._repository.get_category(payload.parent_id) is None:
            raise ValueError("parent category not found")
        c = self._repository.create_category(name=payload.name, parent_id=payload.parent_id)
        return CategoryRead.model_validate(c.__dict__)

    def list_categories(self) -> list[CategoryRead]:
        return [CategoryRead.model_validate(c.__dict__) for c in self._repository.list_categories()]

    def create_product(self, payload: ProductCreate) -> ProductRead:
        if self._repository.get_category(payload.category_id) is None:
            raise ValueError("category not found")
        p = self._repository.create_product(payload.title, payload.category_id, payload.base_price)
        return ProductRead.model_validate(p.__dict__)

    def list_products(self) -> list[ProductRead]:
        return [ProductRead.model_validate(p.__dict__) for p in self._repository.list_products()]

    def create_variant(self, payload: ProductVariantCreate) -> ProductVariantRead:
        if self._repository.get_product(payload.product_id) is None:
            raise ValueError("product not found")
        if self._repository.get_variant_by_sku(payload.sku) is not None:
            raise ValueError("sku already exists")
        v = self._repository.create_variant(payload.product_id, payload.sku, payload.title, payload.base_price)
        return ProductVariantRead.model_validate(v.__dict__)

    def set_inventory(self, payload: InventorySet) -> InventoryRead:
        if self._repository.get_variant(payload.variant_id) is None:
            raise ValueError("variant not found")
        i = self._repository.set_inventory(payload.variant_id, payload.qty)
        return InventoryRead.model_validate(i.__dict__)
    
    def get_inventory(self, variant_id: int) -> InventoryRead | None:
        inv = self._repository.get_inventory(variant_id)
        return InventoryRead.model_validate(inv.__dict__) if inv else None

    def add_attribute(self, payload: ProductAttributeCreate) -> ProductAttributeRead:
        if self._repository.get_product(payload.product_id) is None:
            raise ValueError("product not found")
        attr = self._repository.add_attribute(payload.product_id, payload.name, payload.value)
        return ProductAttributeRead.model_validate(attr.__dict__)