from abc import ABC, abstractmethod
from app.modules.admin.schemas.dto import AdminCreate, AdminRead, AdminUpdate


class AdminService(ABC):
    @abstractmethod
    def list(self) -> list[AdminRead]: ...

    @abstractmethod
    def get(self, item_id: int) -> AdminRead | None: ...

    @abstractmethod
    def create(self, payload: AdminCreate) -> AdminRead: ...

    @abstractmethod
    def update(self, item_id: int, payload: AdminUpdate) -> AdminRead | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...
