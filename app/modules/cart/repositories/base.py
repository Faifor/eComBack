from abc import ABC, abstractmethod
from app.modules.cart.models.entity import CartEntity


class CartRepository(ABC):
    @abstractmethod
    def list(self) -> list[CartEntity]: ...

    @abstractmethod
    def get(self, item_id: int) -> CartEntity | None: ...

    @abstractmethod
    def create(self, name: str) -> CartEntity: ...

    @abstractmethod
    def update(self, item_id: int, name: str) -> CartEntity | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...
