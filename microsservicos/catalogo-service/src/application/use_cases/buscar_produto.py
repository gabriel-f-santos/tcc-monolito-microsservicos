from uuid import UUID

from src.domain.entities.produto import Produto
from src.domain.exceptions.catalogo import ProdutoNaoEncontrado
from src.domain.repositories.produto_repository import ProdutoRepository


class BuscarProdutoUseCase:
    def __init__(self, repo: ProdutoRepository) -> None:
        self.repo = repo

    def execute(self, produto_id: UUID) -> Produto:
        produto = self.repo.get_by_id(produto_id)
        if produto is None:
            raise ProdutoNaoEncontrado()
        return produto
