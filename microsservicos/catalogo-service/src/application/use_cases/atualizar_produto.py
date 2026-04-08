from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.domain.entities.produto import Produto
from src.domain.exceptions.catalogo import ProdutoNaoEncontrado
from src.domain.repositories.produto_repository import ProdutoRepository


@dataclass
class AtualizarProdutoDTO:
    nome: str | None = None
    descricao: str | None = None
    preco: Decimal | None = None


class AtualizarProdutoUseCase:
    def __init__(self, repo: ProdutoRepository) -> None:
        self.repo = repo

    def execute(self, produto_id: UUID, dados: AtualizarProdutoDTO) -> Produto:
        produto = self.repo.get_by_id(produto_id)
        if produto is None:
            raise ProdutoNaoEncontrado()

        produto.atualizar(
            nome=dados.nome,
            descricao=dados.descricao,
            preco=dados.preco,
        )
        return self.repo.save(produto)
