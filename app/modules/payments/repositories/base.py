from abc import ABC, abstractmethod
from app.modules.payments.models.entity import PaymentsEntity


class PaymentsRepository(ABC):
    @abstractmethod
    def list(self) -> list[PaymentsEntity]: ...

    @abstractmethod
    def get(self, item_id: int) -> PaymentsEntity | None: ...

    @abstractmethod
    def create(self, name: str) -> PaymentsEntity: ...

    @abstractmethod
    def update(self, item_id: int, name: str) -> PaymentsEntity | None: ...

    @abstractmethod
    def delete(self, item_id: int) -> bool: ...