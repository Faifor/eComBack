from abc import ABC, abstractmethod
from app.modules.catalog.schemas.dto import CatalogCreate, CatalogRead, CatalogUpdate


class CatalogService(ABC):
    @abstractmethod
    def list(self) -> list[CatalogRead]: ...

    @abstractmethod
    def get(self, item_id: int) -> CatalogRead | None: ...

    @abstractmethod
    def create(self, payload: CatalogCreate) -> CatalogRead: ...

    @abstractmethod
    def update(self, item_id: int, payload: CatalogUpdate) -> CatalogRead | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...
