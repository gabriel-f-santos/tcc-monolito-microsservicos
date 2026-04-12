from uuid import UUID

from src.estoque.domain.entities.alerta_estoque import AlertaEstoque
from src.estoque.domain.exceptions.estoque import ItemNaoEncontrado
from src.estoque.domain.repositories.alerta_estoque_repository import AlertaEstoqueRepository
from src.estoque.domain.repositories.item_estoque_repository import ItemEstoqueRepository


class ListarAlertasUseCase:
    def __init__(
        self,
        item_repo: ItemEstoqueRepository,
        alerta_repo: AlertaEstoqueRepository,
    ) -> None:
        self.item_repo = item_repo
        self.alerta_repo = alerta_repo

    def execute(self, item_estoque_id: UUID) -> list[AlertaEstoque]:
        item = self.item_repo.get_by_id(item_estoque_id)
        if item is None:
            raise ItemNaoEncontrado()
        return self.alerta_repo.list_by_item(item_estoque_id)
