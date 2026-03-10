from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.modules.auth.dependencies import require_role
from app.modules.auth.models.entity import UserRole
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
from app.modules.catalog.services.service import DefaultCatalogService

from app.modules.runtime import catalog_repository


router = APIRouter(
    prefix="/catalog",
    tags=["catalog-user"],
    dependencies=[Depends(require_role(UserRole.USER, UserRole.ADMIN))],
)
_service = DefaultCatalogService(catalog_repository)


@router.post(
    "/categories",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def create_category(payload: CategoryCreate) -> CategoryRead:
    try:
        return _service.create_category(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

@router.get("/categories", response_model=list[CategoryRead])
def list_categories() -> list[CategoryRead]:
    return _service.list_categories()


@router.post(
    "/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def create_product(payload: ProductCreate) -> ProductRead:
    try:
        return _service.create_product(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/products", response_model=list[ProductRead])
def list_products(
    category_id: int | None = Query(default=None, gt=0),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    q: str | None = None,
    sort_by: str = Query(default="id", pattern="^(id|title|base_price|average_rating|reviews_count)$"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
) -> list[ProductRead]:
    return _service.list_products(
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        q=q,
        sort_by=sort_by,
        sort_order=sort_order,
    )





@router.get("/products/{product_id}/variants", response_model=list[ProductVariantRead])
def list_product_variants(product_id: int) -> list[ProductVariantRead]:
    try:
        details = _service.get_product_details(product_id)
        return details.variants
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/products/{product_id}", response_model=ProductDetailsRead)
def get_product_details(product_id: int) -> ProductDetailsRead:
    try:
        return _service.get_product_details(product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/variants",
    response_model=ProductVariantRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def create_variant(payload: ProductVariantCreate) -> ProductVariantRead:
    try:
        return _service.create_variant(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put(
    "/inventory",
    response_model=InventoryRead,
    include_in_schema=False,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def set_inventory(payload: InventorySet) -> InventoryRead:
    try:
        return _service.set_inventory(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post(
    "/attributes",
    response_model=ProductAttributeRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def add_attribute(payload: ProductAttributeCreate) -> ProductAttributeRead:
    try:
        return _service.add_attribute(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/products/{product_id}/reviews", response_model=ProductReviewRead, status_code=status.HTTP_201_CREATED)
def add_product_review(product_id: int, payload: ProductReviewCreate) -> ProductReviewRead:
    try:
        return _service.add_review(product_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/products/{product_id}/reviews", response_model=list[ProductReviewRead])
def list_product_reviews(product_id: int) -> list[ProductReviewRead]:
    try:
        return _service.list_reviews(product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
