from app.modules.cart.repositories.memory import InMemoryCartRepository
from app.modules.catalog.repositories.sqlalchemy import SQLAlchemyCatalogRepository
from app.modules.orders.repositories.sqlalchemy import SQLAlchemyOrdersRepository
from app.modules.pricing.repositories.sqlalchemy import SQLAlchemyPricingRepository
from app.modules.pricing.services.service import DefaultPricingService

catalog_repository = SQLAlchemyCatalogRepository()
pricing_repository = SQLAlchemyPricingRepository()
cart_repository = InMemoryCartRepository()
orders_repository = SQLAlchemyOrdersRepository()

pricing_service = DefaultPricingService(pricing_repository, catalog_repository)