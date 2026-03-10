from app.modules.catalog.repositories.base import CatalogRepository
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

    def delete_category(self, category_id: int) -> None:
        self._repository.delete_category(category_id)

    def create_product(self, payload: ProductCreate) -> ProductRead:
        if self._repository.get_category(payload.category_id) is None:
            raise ValueError("category not found")
        p = self._repository.create_product(payload.title, payload.category_id, payload.base_price, payload.description)
        return ProductRead.model_validate(p.__dict__)

    def list_products(
        self,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        q: str | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> list[ProductRead]:
        products: list[ProductRead] = []
        for product in self._repository.list_products():
            payload = ProductRead.model_validate(product.__dict__)
            payload.images = [ProductImageRead.model_validate(image.__dict__) for image in self._repository.list_product_images(product.id)]
            summary = self._repository.get_product_rating_summary(product.id)
            payload.average_rating = summary.average_rating
            payload.reviews_count = summary.reviews_count
            products.append(payload)

        if category_id is not None:
            products = [item for item in products if item.category_id == category_id]
        if min_price is not None:
            products = [item for item in products if float(item.base_price) >= min_price]
        if max_price is not None:
            products = [item for item in products if float(item.base_price) <= max_price]
        if q:
            query = q.lower()
            products = [item for item in products if query in item.title.lower()]

        reverse = sort_order == "desc"
        sort_key_map = {
            "id": lambda item: item.id,
            "title": lambda item: item.title.lower(),
            "base_price": lambda item: float(item.base_price),
            "average_rating": lambda item: item.average_rating,
            "reviews_count": lambda item: item.reviews_count,
        }
        key = sort_key_map.get(sort_by, sort_key_map["id"])
        return sorted(products, key=key, reverse=reverse)

    def delete_product(self, product_id: int) -> None:
        self._repository.delete_product(product_id)


    def get_product_details(self, product_id: int) -> ProductDetailsRead:
        product = self._repository.get_product(product_id)
        if product is None:
            raise ValueError("product not found")
        payload = ProductDetailsRead.model_validate(product.__dict__)
        payload.images = [ProductImageRead.model_validate(image.__dict__) for image in self._repository.list_product_images(product_id)]
        payload.attributes = [ProductAttributeRead.model_validate(attr.__dict__) for attr in self._repository.list_attributes(product_id)]
        payload.variants = [ProductVariantRead.model_validate(variant.__dict__) for variant in self._repository.list_variants_by_product(product_id)]
        payload.reviews = [ProductReviewRead.model_validate(review.__dict__) for review in self._repository.list_product_reviews(product_id)]
        summary = self._repository.get_product_rating_summary(product_id)
        payload.average_rating = summary.average_rating
        payload.reviews_count = summary.reviews_count
        return payload

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
        if payload.variant_id is not None:
            variant = self._repository.get_variant(payload.variant_id)
            if variant is None:
                raise ValueError("variant not found")
            if variant.product_id != payload.product_id:
                raise ValueError("variant does not belong to product")
        attr = self._repository.add_attribute(payload.product_id, payload.name, payload.value, payload.variant_id)
        return ProductAttributeRead.model_validate(attr.__dict__)

    def add_product_image(self, product_id: int, image_url: str, is_primary: bool = False, sort_order: int = 0) -> ProductImageRead:
        if self._repository.get_product(product_id) is None:
            raise ValueError("product not found")
        image = self._repository.add_product_image(product_id, image_url, is_primary, sort_order)
        return ProductImageRead.model_validate(image.__dict__)

    def add_review(self, product_id: int, payload: ProductReviewCreate) -> ProductReviewRead:
        if self._repository.get_product(product_id) is None:
            raise ValueError("product not found")
        review = self._repository.add_product_review(product_id, payload.user_id, payload.rating, payload.review)
        return ProductReviewRead.model_validate(review.__dict__)

    def list_reviews(self, product_id: int) -> list[ProductReviewRead]:
        if self._repository.get_product(product_id) is None:
            raise ValueError("product not found")
        return [ProductReviewRead.model_validate(review.__dict__) for review in self._repository.list_product_reviews(product_id)]
