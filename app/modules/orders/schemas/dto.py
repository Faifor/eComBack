from pydantic import BaseModel


class OrdersCreate(BaseModel):
    name: str


class OrdersUpdate(BaseModel):
    name: str | None = None


class OrdersRead(BaseModel):
    id: int
    name: str
    