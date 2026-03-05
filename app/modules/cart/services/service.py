from app.modules.cart.repositories.base import CartRepository
from app.modules.cart.schemas.dto import CartCreate, CartRead, CartUpdate
from app.modules.cart.services.base import CartService


class DefaultCartService(CartService):
    def __init__(self, repository: CartRepository) -> None:
        self._repository = repository

    def list(self) -> list[CartRead]:
        return [CartRead(id=item.id, name=item.name) for item in self._repository.list()]

    def get(self, item_id: int) -> CartRead | None:
        item = self._repository.get(item_id)
        if item is None:
            return None
        return CartRead(id=item.id, name=item.name)

    def create(self, payload: CartCreate) -> CartRead:
        item = self._repository.create(name=payload.name)
        return CartRead(id=item.id, name=item.name)

    def update(self, item_id: int, payload: CartUpdate) -> CartRead | None:
        current = self._repository.get(item_id)
        if current is None:
            return None

        name = payload.name if payload.name is not None else current.name
        item = self._repository.update(item_id=item_id, name=name)
        if item is None:
            return None
        return CartRead(id=item.id, name=item.name)

    def delete(self, item_id: int) -> bool:
        return self._repository.delete(item_id)
