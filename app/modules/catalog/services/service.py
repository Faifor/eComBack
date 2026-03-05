from app.modules.catalog.repositories.base import CatalogRepository
from app.modules.catalog.schemas.dto import CatalogCreate, CatalogRead, CatalogUpdate
from app.modules.catalog.services.base import CatalogService


class DefaultCatalogService(CatalogService):
    def __init__(self, repository: CatalogRepository) -> None:
        self._repository = repository

    def list(self) -> list[CatalogRead]:
        return [CatalogRead(id=item.id, name=item.name) for item in self._repository.list()]

    def get(self, item_id: int) -> CatalogRead | None:
        item = self._repository.get(item_id)
        if item is None:
            return None
        return CatalogRead(id=item.id, name=item.name)

    def create(self, payload: CatalogCreate) -> CatalogRead:
        item = self._repository.create(name=payload.name)
        return CatalogRead(id=item.id, name=item.name)

    def update(self, item_id: int, payload: CatalogUpdate) -> CatalogRead | None:
        current = self._repository.get(item_id)
        if current is None:
            return None

        name = payload.name if payload.name is not None else current.name
        item = self._repository.update(item_id=item_id, name=name)
        if item is None:
            return None
        return CatalogRead(id=item.id, name=item.name)

    def delete(self, item_id: int) -> bool:
        return self._repository.delete(item_id)