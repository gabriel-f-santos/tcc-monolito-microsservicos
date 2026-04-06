from uuid import UUID

from src.catalogo.domain.entities.produto import Produto
from src.catalogo.domain.repositories.produto_repository import ProdutoRepository


class ListarProdutosUseCase:
    def __init__(self, repo: ProdutoRepository) -> None:
        self.repo = repo

    def execute(
        self,
        categoria_id: UUID | None = None,
        ativo: bool | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Produto]:
        return self.repo.list_filtered(
            categoria_id=categoria_id,
            ativo=ativo,
            page=page,
            size=size,
        )
