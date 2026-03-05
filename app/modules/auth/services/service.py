from app.modules.auth.repositories.base import AuthRepository
from app.modules.auth.schemas.dto import AuthCreate, AuthRead, AuthUpdate
from app.modules.auth.services.base import AuthService


class DefaultAuthService(AuthService):
    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository

    def list(self) -> list[AuthRead]:
        return [AuthRead(id=item.id, name=item.name) for item in self._repository.list()]

    def get(self, item_id: int) -> AuthRead | None:
        item = self._repository.get(item_id)
        if item is None:
            return None
        return AuthRead(id=item.id, name=item.name)

    def create(self, payload: AuthCreate) -> AuthRead:
        item = self._repository.create(name=payload.name)
        return AuthRead(id=item.id, name=item.name)

    def update(self, item_id: int, payload: AuthUpdate) -> AuthRead | None:
        current = self._repository.get(item_id)
        if current is None:
            return None

        name = payload.name if payload.name is not None else current.name
        item = self._repository.update(item_id=item_id, name=name)
        if item is None:
            return None
        return AuthRead(id=item.id, name=item.name)

    def delete(self, item_id: int) -> bool:
        return self._repository.delete(item_id)
