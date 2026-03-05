from pydantic import BaseModel


class CatalogCreate(BaseModel):
    name: str


class CatalogUpdate(BaseModel):
    name: str | None = None


class CatalogRead(BaseModel):
    id: int
    name: str