from app.modules.cart.repositories.memory import InMemoryCartRepository
from app.modules.catalog.repositories.memory import InMemoryCatalogRepository
from app.modules.orders.repositories.memory import InMemoryOrdersRepository
from app.modules.pricing.repositories.memory import InMemoryPricingRepository
from app.modules.pricing.services.service import DefaultPricingService

catalog_repository = InMemoryCatalogRepository()
pricing_repository = InMemoryPricingRepository()
cart_repository = InMemoryCartRepository()
orders_repository = InMemoryOrdersRepository()

pricing_service = DefaultPricingService(pricing_repository, catalog_repository)