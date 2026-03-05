from abc import ABC, abstractmethod
from app.modules.cart.schemas.dto import CartCreate, CartRead, CartUpdate


class CartService(ABC):
    @abstractmethod
    def list(self) -> list[CartRead]: ...

    @abstractmethod
    def get(self, item_id: int) -> CartRead | None: ...

    @abstractmethod
    def create(self, payload: CartCreate) -> CartRead: ...

    @abstractmethod
    def update(self, item_id: int, payload: CartUpdate) -> CartRead | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...
