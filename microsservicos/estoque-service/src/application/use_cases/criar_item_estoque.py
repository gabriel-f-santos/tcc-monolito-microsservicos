from uuid import UUID

from src.domain.entities.item_estoque import ItemEstoque
from src.domain.repositories.item_estoque_repository import ItemEstoqueRepository


class CriarItemEstoqueUseCase:
    def __init__(self, repo: ItemEstoqueRepository) -> None:
        self.repo = repo

    def execute(self, dados: dict) -> ItemEstoque:
        produto_id = UUID(dados["produto_id"])

        existing = self.repo.get_by_produto_id(produto_id)
        if existing is not None:
            return existing

        item = ItemEstoque(
            produto_id=produto_id,
            sku=dados["sku"],
            nome_produto=dados["nome"],
            categoria_nome=dados["categoria_nome"],
            saldo=0,
            ativo=True,
        )
        return self.repo.save(item)
