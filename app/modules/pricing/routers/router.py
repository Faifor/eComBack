from fastapi import APIRouter, HTTPException, status

from app.modules.pricing.schemas.dto import (
    PriceCalculateRequest,
    PriceCalculateResponse,
    PricingRuleCreate,
    PricingRuleRead,
)
from app.modules.runtime import pricing_service


router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.post("/rules", response_model=PricingRuleRead, status_code=status.HTTP_201_CREATED)
def create_rule(payload: PricingRuleCreate) -> PricingRuleRead:
    return pricing_service.create_rule(payload)


@router.get("/rules", response_model=list[PricingRuleRead])
def list_rules() -> list[PricingRuleRead]:
    return pricing_service.list_rules()


@router.post("/calculate", response_model=PriceCalculateResponse)
def calculate(payload: PriceCalculateRequest) -> PriceCalculateResponse:
    try:
        return pricing_service.calculate_price(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc