from uuid import UUID

from src.estoque.domain.entities.item_estoque import ItemEstoque
from src.estoque.domain.exceptions.estoque import ItemNaoEncontrado
from src.estoque.domain.repositories.item_estoque_repository import ItemEstoqueRepository


class BuscarItemUseCase:
    def __init__(self, repo: ItemEstoqueRepository) -> None:
        self.repo = repo

    def execute(self, item_id: UUID) -> ItemEstoque:
        item = self.repo.get_by_id(item_id)
        if item is None:
            raise ItemNaoEncontrado()
        return item

    def execute_por_produto(self, produto_id: UUID) -> ItemEstoque:
        item = self.repo.get_by_produto_id(produto_id)
        if item is None:
            raise ItemNaoEncontrado()
        return item
