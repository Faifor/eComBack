from abc import ABC, abstractmethod
from app.modules.payments.schemas.dto import PaymentsCreate, PaymentsRead, PaymentsUpdate


class PaymentsService(ABC):
    @abstractmethod
    def list(self) -> list[PaymentsRead]: ...

    @abstractmethod
    def get(self, item_id: int) -> PaymentsRead | None: ...

    @abstractmethod
    def create(self, payload: PaymentsCreate) -> PaymentsRead: ...

    @abstractmethod
    def update(self, item_id: int, payload: PaymentsUpdate) -> PaymentsRead | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...