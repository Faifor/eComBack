from abc import ABC, abstractmethod

from app.modules.cart.models.entity import Cart, CartItem


class CartRepository(ABC):
    @abstractmethod
    def create_cart(self, user_id: int) -> Cart: ...

    @abstractmethod
    def get_cart(self, cart_id: int) -> Cart | None: ...

    @abstractmethod
    def upsert_item(self, cart_id: int, variant_id: int, sku: str, title: str, qty: int, unit_price, total_price, rule_trace) -> CartItem: ...