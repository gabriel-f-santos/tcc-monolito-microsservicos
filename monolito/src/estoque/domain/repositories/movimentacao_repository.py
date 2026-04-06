from abc import ABC, abstractmethod
from uuid import UUID

from src.estoque.domain.entities.movimentacao import Movimentacao


class MovimentacaoRepository(ABC):
    @abstractmethod
    def save(self, entity: Movimentacao) -> Movimentacao:
        ...

    @abstractmethod
    def list_by_item(
        self,
        item_estoque_id: UUID,
        tipo: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Movimentacao]:
        ...
