from pydantic import BaseModel


class AiCreate(BaseModel):
    name: str


class AiUpdate(BaseModel):
    name: str | None = None


class AiRead(BaseModel):
    id: int
    name: str
