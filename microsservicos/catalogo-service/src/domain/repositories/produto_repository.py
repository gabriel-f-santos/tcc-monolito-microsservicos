from abc import abstractmethod
from uuid import UUID

from src.domain.entities.produto import Produto
from src.shared.domain.repositories.base import BaseRepository


class ProdutoRepository(BaseRepository[Produto]):
    @abstractmethod
    def get_by_sku(self, sku: str) -> Produto | None:
        ...

    @abstractmethod
    def list_filtered(
        self,
        categoria_id: UUID | None = None,
        ativo: bool | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Produto]:
        ...
