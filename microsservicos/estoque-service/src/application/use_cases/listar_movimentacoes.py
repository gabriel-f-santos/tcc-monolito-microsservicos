from uuid import UUID

from src.domain.entities.movimentacao import Movimentacao
from src.domain.exceptions.estoque import ItemNaoEncontrado
from src.domain.repositories.item_estoque_repository import ItemEstoqueRepository
from src.domain.repositories.movimentacao_repository import MovimentacaoRepository


class ListarMovimentacoesUseCase:
    def __init__(
        self,
        item_repo: ItemEstoqueRepository,
        mov_repo: MovimentacaoRepository,
    ) -> None:
        self.item_repo = item_repo
        self.mov_repo = mov_repo

    def execute(
        self,
        item_estoque_id: UUID,
        tipo: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Movimentacao]:
        item = self.item_repo.get_by_id(item_estoque_id)
        if item is None:
            raise ItemNaoEncontrado()

        return self.mov_repo.list_by_item(
            item_estoque_id=item_estoque_id,
            tipo=tipo,
            page=page,
            size=size,
        )
