from pydantic import BaseModel


class CartCreate(BaseModel):
    name: str


class CartUpdate(BaseModel):
    name: str | None = None


class CartRead(BaseModel):
    id: int
    name: str