from abc import ABC, abstractmethod

from app.modules.cart.schemas.dto import CartCreate, CartItemUpsert, CartRead

class CartService(ABC):
    @abstractmethod
    def create_cart(self, payload: CartCreate) -> CartRead: ...

    @abstractmethod
    def get_cart(self, cart_id: int) -> CartRead | None: ...

    @abstractmethod
    def upsert_item(self, cart_id: int, payload: CartItemUpsert) -> CartRead: ...