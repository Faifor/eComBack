from app.modules.cart.models.entity import Cart, CartItem
from app.modules.cart.repositories.base import CartRepository


class InMemoryCartRepository(CartRepository):
    def __init__(self) -> None:
        self._carts: dict[int, Cart] = {}
        self._next_cart_id = 1
        self._next_item_id = 1

    def create_cart(self, user_id: int) -> Cart:
        cart = Cart(id=self._next_cart_id, user_id=user_id)
        self._carts[cart.id] = cart
        self._next_cart_id += 1
        return cart

    def get_cart(self, cart_id: int) -> Cart | None:
        return self._carts.get(cart_id)

    def upsert_item(self, cart_id: int, variant_id: int, sku: str, title: str, qty: int, unit_price, total_price, rule_trace) -> CartItem:
        cart = self._carts[cart_id]
        existing = next((item for item in cart.items if item.variant_id == variant_id), None)
        if existing is None:
            existing = CartItem(
                id=self._next_item_id,
                cart_id=cart_id,
                variant_id=variant_id,
                sku=sku,
                title=title,
                qty=qty,
                unit_price=unit_price,
                total_price=total_price,
                rule_trace=rule_trace,
            )
            self._next_item_id += 1
            cart.items.append(existing)
        else:
            existing.qty = qty
            existing.unit_price = unit_price
            existing.total_price = total_price
            existing.rule_trace = rule_trace

        if qty <= 0:
            cart.items = [item for item in cart.items if item.variant_id != variant_id]
        return existing