from pydantic import BaseModel


class PricingCreate(BaseModel):
    name: str


class PricingUpdate(BaseModel):
    name: str | None = None


class PricingRead(BaseModel):
    id: int
    name: str
