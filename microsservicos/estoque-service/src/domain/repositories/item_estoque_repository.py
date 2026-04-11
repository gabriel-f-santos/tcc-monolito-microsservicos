from abc import abstractmethod
from uuid import UUID

from src.domain.entities.item_estoque import ItemEstoque
from src.shared.domain.repositories.base import BaseRepository


class ItemEstoqueRepository(BaseRepository[ItemEstoque]):
    @abstractmethod
    def get_by_produto_id(self, produto_id: UUID) -> ItemEstoque | None:
        ...

    @abstractmethod
    def list_filtered(
        self,
        saldo_min: int | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[ItemEstoque]:
        ...
