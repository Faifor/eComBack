from pydantic import BaseModel


class PaymentsCreate(BaseModel):
    name: str


class PaymentsUpdate(BaseModel):
    name: str | None = None


class PaymentsRead(BaseModel):
    id: int
    name: str