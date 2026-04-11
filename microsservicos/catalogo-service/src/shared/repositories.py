from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from src.shared.entities import BaseEntity

T = TypeVar("T", bound=BaseEntity)


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def get_by_id(self, entity_id: UUID) -> T | None:
        ...

    @abstractmethod
    def save(self, entity: T) -> T:
        ...

    @abstractmethod
    def delete(self, entity_id: UUID) -> None:
        ...
