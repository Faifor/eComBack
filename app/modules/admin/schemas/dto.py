from pydantic import BaseModel


class AdminCreate(BaseModel):
    name: str


class AdminUpdate(BaseModel):
    name: str | None = None


class AdminRead(BaseModel):
    id: int
    name: str