from src.estoque.domain.entities.item_estoque import ItemEstoque
from src.estoque.domain.repositories.item_estoque_repository import ItemEstoqueRepository


class ListarItensUseCase:
    def __init__(self, repo: ItemEstoqueRepository) -> None:
        self.repo = repo

    def execute(
        self,
        saldo_min: int | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[ItemEstoque]:
        return self.repo.list_filtered(saldo_min=saldo_min, page=page, size=size)
