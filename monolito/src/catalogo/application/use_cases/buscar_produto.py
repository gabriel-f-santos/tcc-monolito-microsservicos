from uuid import UUID

from src.catalogo.domain.entities.produto import Produto
from src.catalogo.domain.exceptions.catalogo import ProdutoNaoEncontrado
from src.catalogo.domain.repositories.produto_repository import ProdutoRepository


class BuscarProdutoUseCase:
    def __init__(self, repo: ProdutoRepository) -> None:
        self.repo = repo

    def execute(self, produto_id: UUID) -> Produto:
        produto = self.repo.get_by_id(produto_id)
        if produto is None:
            raise ProdutoNaoEncontrado()
        return produto
