from app.modules.auth.routers.router import router as auth_router
from app.modules.catalog.routers.router import router as catalog_router
from app.modules.pricing.routers.router import router as pricing_router
from app.modules.cart.routers.router import router as cart_router
from app.modules.orders.routers.router import router as orders_router
from app.modules.payments.routers.router import router as payments_router
from app.modules.admin.routers.router import router as admin_router
from app.modules.ai.routers.router import router as ai_router

from fastapi import APIRouter

router = APIRouter(prefix='/api/v1')

router.include_router(auth_router)
router.include_router(catalog_router)
router.include_router(pricing_router)
router.include_router(cart_router)
router.include_router(orders_router)
router.include_router(payments_router)
router.include_router(admin_router)
router.include_router(ai_router)
