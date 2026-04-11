from abc import abstractmethod
from uuid import UUID

from src.domain.entities import Categoria, Produto
from src.shared.repositories import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    @abstractmethod
    def get_by_nome(self, nome: str) -> Categoria | None:
        ...

    @abstractmethod
    def list_all(self) -> list[Categoria]:
        ...


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
