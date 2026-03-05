from abc import ABC, abstractmethod
from app.modules.catalog.models.entity import CatalogEntity


class CatalogRepository(ABC):
    @abstractmethod
    def list(self) -> list[CatalogEntity]: ...

    @abstractmethod
    def get(self, item_id: int) -> CatalogEntity | None: ...

    @abstractmethod
    def create(self, name: str) -> CatalogEntity: ...

    @abstractmethod
    def update(self, item_id: int, name: str) -> CatalogEntity | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...