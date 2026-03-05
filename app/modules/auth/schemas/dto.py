from pydantic import BaseModel


class AuthCreate(BaseModel):
    name: str


class AuthUpdate(BaseModel):
    name: str | None = None


class AuthRead(BaseModel):
    id: int
    name: str
