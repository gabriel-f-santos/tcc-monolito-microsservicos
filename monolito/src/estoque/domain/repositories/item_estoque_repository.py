from abc import abstractmethod
from uuid import UUID

from src.estoque.domain.entities.item_estoque import ItemEstoque
from src.shared.domain.repositories.base import BaseRepository


class ItemEstoqueRepository(BaseRepository[ItemEstoque]):
    @abstractmethod
    def get_by_produto_id(self, produto_id: UUID) -> ItemEstoque | None:
        ...
