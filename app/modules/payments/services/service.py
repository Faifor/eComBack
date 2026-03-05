from app.modules.payments.repositories.base import PaymentsRepository
from app.modules.payments.schemas.dto import PaymentsCreate, PaymentsRead, PaymentsUpdate
from app.modules.payments.services.base import PaymentsService


class DefaultPaymentsService(PaymentsService):
    def __init__(self, repository: PaymentsRepository) -> None:
        self._repository = repository

    def list(self) -> list[PaymentsRead]:
        return [PaymentsRead(id=item.id, name=item.name) for item in self._repository.list()]

    def get(self, item_id: int) -> PaymentsRead | None:
        item = self._repository.get(item_id)
        if item is None:
            return None
        return PaymentsRead(id=item.id, name=item.name)

    def create(self, payload: PaymentsCreate) -> PaymentsRead:
        item = self._repository.create(name=payload.name)
        return PaymentsRead(id=item.id, name=item.name)

    def update(self, item_id: int, payload: PaymentsUpdate) -> PaymentsRead | None:
        current = self._repository.get(item_id)
        if current is None:
            return None

        name = payload.name if payload.name is not None else current.name
        item = self._repository.update(item_id=item_id, name=name)
        if item is None:
            return None
        return PaymentsRead(id=item.id, name=item.name)

    def delete(self, item_id: int) -> bool:
        return self._repository.delete(item_id)
