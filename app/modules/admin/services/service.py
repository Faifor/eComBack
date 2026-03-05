from app.modules.admin.repositories.base import AdminRepository
from app.modules.admin.schemas.dto import AdminCreate, AdminRead, AdminUpdate
from app.modules.admin.services.base import AdminService


class DefaultAdminService(AdminService):
    def __init__(self, repository: AdminRepository) -> None:
        self._repository = repository

    def list(self) -> list[AdminRead]:
        return [AdminRead(id=item.id, name=item.name) for item in self._repository.list()]

    def get(self, item_id: int) -> AdminRead | None:
        item = self._repository.get(item_id)
        if item is None:
            return None
        return AdminRead(id=item.id, name=item.name)

    def create(self, payload: AdminCreate) -> AdminRead:
        item = self._repository.create(name=payload.name)
        return AdminRead(id=item.id, name=item.name)

    def update(self, item_id: int, payload: AdminUpdate) -> AdminRead | None:
        current = self._repository.get(item_id)
        if current is None:
            return None

        name = payload.name if payload.name is not None else current.name
        item = self._repository.update(item_id=item_id, name=name)
        if item is None:
            return None
        return AdminRead(id=item.id, name=item.name)

    def delete(self, item_id: int) -> bool:
        return self._repository.delete(item_id)