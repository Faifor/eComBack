import hashlib
import hmac

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.core.config import YOOKASSA_WEBHOOK_SECRET
from app.modules.orders.services.service import DefaultOrdersService
from app.modules.payments.services.yookassa_client import YooKassaClient
from app.modules.runtime import cart_repository, catalog_repository, orders_repository

router = APIRouter(prefix='/payments', tags=['payments'])
_orders_service = DefaultOrdersService(orders_repository, cart_repository, YooKassaClient(), catalog_repository)

@router.post('/yookassa/webhook', status_code=status.HTTP_200_OK)
async def yookassa_webhook(
    request: Request,
    x_yookassa_signature: str | None = Header(default=None),
    x_webhook_secret: str | None = Header(default=None),
) -> dict[str, str]:
    body = await request.body()
    if not _validate_webhook_secret(body, x_yookassa_signature, x_webhook_secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid webhook signature')

    payload = await request.json()
    payment_obj = payload.get('object') or {}
    payment_id = payment_obj.get('id')
    payment_status = payment_obj.get('status')

    if not payment_id or not payment_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid webhook payload')


    order = _orders_service.process_payment_webhook(payment_id=payment_id, payment_status=payment_status)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='order not found for payment')
    
    return {'result': 'ok'}


def _validate_webhook_secret(body: bytes, signature: str | None, header_secret: str | None) -> bool:
    if not YOOKASSA_WEBHOOK_SECRET:
        return False


    if header_secret and hmac.compare_digest(header_secret, YOOKASSA_WEBHOOK_SECRET):
        return True
    
    if signature:
        digest = hmac.new(YOOKASSA_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, digest)
    
    return False