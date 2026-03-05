from app.modules.cart.repositories.base import CartRepository
from app.modules.cart.schemas.dto import CartCreate, CartItemRead, CartItemUpsert, CartRead
from app.modules.cart.services.base import CartService
from app.modules.catalog.repositories.base import CatalogRepository
from app.modules.pricing.schemas.dto import PriceCalculateRequest
from app.modules.pricing.services.base import PricingService


class DefaultCartService(CartService):
    def __init__(self, repository: CartRepository, catalog_repository: CatalogRepository, pricing_service: PricingService) -> None:
        self._repository = repository

        self._catalog_repository = catalog_repository
        self._pricing_service = pricing_service

    def create_cart(self, payload: CartCreate) -> CartRead:
        cart = self._repository.create_cart(payload.user_id)
        return self._to_read(cart)

    def get_cart(self, cart_id: int) -> CartRead | None:
        cart = self._repository.get_cart(cart_id)
        return self._to_read(cart) if cart else None

    def upsert_item(self, cart_id: int, payload: CartItemUpsert) -> CartRead:
        cart = self._repository.get_cart(cart_id)
        if cart is None:
            raise ValueError("cart not found")

        variant = self._catalog_repository.get_variant(payload.variant_id)
        if variant is None:
            raise ValueError("variant not found")

        inventory = self._catalog_repository.get_inventory(payload.variant_id)
        if payload.qty > 0 and inventory is not None and payload.qty > inventory.qty:
            raise ValueError("insufficient inventory")

        price = self._pricing_service.calculate_price(
            PriceCalculateRequest(variant_id=payload.variant_id, qty=max(payload.qty, 1), promo_code=payload.promo_code)
        )
        self._repository.upsert_item(
            cart_id=cart_id,
            variant_id=payload.variant_id,
            sku=variant.sku,
            title=variant.title,
            qty=payload.qty,
            unit_price=price.unit_price,
            total_price=price.unit_price * payload.qty,
            rule_trace=[item.model_dump() for item in price.applied_rules],
        )
        return self._to_read(self._repository.get_cart(cart_id))

    def _to_read(self, cart) -> CartRead:
        return CartRead(
            id=cart.id,
            user_id=cart.user_id,
            currency=cart.currency,
            items=[CartItemRead.model_validate(item.__dict__) for item in cart.items],
        )