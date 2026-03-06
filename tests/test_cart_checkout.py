import asyncio
import sys
import types

httpx_stub = types.ModuleType("httpx")
httpx_stub.AsyncClient = object
sys.modules.setdefault("httpx", httpx_stub)

from app.modules.cart.repositories.memory import InMemoryCartRepository
from app.modules.cart.schemas.dto import CartCreate, CartItemUpsert
from app.modules.cart.services.service import DefaultCartService
from app.modules.catalog.repositories.memory import InMemoryCatalogRepository
from app.modules.orders.models.entity import PaymentMethod
from app.modules.orders.repositories.memory import InMemoryOrdersRepository
from app.modules.orders.schemas.dto import CheckoutRequest
from app.modules.orders.services.service import DefaultOrdersService
from app.modules.pricing.repositories.memory import InMemoryPricingRepository
from app.modules.pricing.services.service import DefaultPricingService


class DummyYooKassaClient:
    async def create_payment_intent(self, amount, idempotence_key: str, description: str):
        return {"id": "mock", "status": "pending"}


def test_cart_checkout_cod_flow() -> None:
    catalog = InMemoryCatalogRepository()
    pricing = DefaultPricingService(InMemoryPricingRepository(), catalog)
    cart_repo = InMemoryCartRepository()
    orders_repo = InMemoryOrdersRepository()

    category = catalog.create_category("Shoes", None)
    product = catalog.create_product("Sneakers", category.id, 5000)
    variant = catalog.create_variant(product.id, "SNK-1", "Sneakers 42", 5500)
    catalog.set_inventory(variant.id, 10)

    cart_service = DefaultCartService(cart_repo, catalog, pricing)
    cart = cart_service.create_cart(CartCreate(user_id=7))
    cart = cart_service.upsert_item(cart.id, CartItemUpsert(variant_id=variant.id, qty=2, promo_code=None))

    orders_service = DefaultOrdersService(orders_repo, cart_repo, DummyYooKassaClient())
    order = asyncio.run(orders_service.checkout(CheckoutRequest(cart_id=cart.id, payment_method=PaymentMethod.cod)))

    assert order.status.value == "awaiting_cod_payment"
    assert order.total_price > 0