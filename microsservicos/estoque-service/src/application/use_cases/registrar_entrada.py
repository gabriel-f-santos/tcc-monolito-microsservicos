from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.movimentacao import Movimentacao
from src.domain.exceptions.estoque import ItemNaoEncontrado
from src.domain.repositories.item_estoque_repository import ItemEstoqueRepository
from src.domain.repositories.movimentacao_repository import MovimentacaoRepository


@dataclass
class RegistrarEntradaDTO:
    item_estoque_id: UUID
    quantidade: int
    lote: str | None = None
    motivo: str | None = None


class RegistrarEntradaUseCase:
    def __init__(
        self,
        item_repo: ItemEstoqueRepository,
        mov_repo: MovimentacaoRepository,
    ) -> None:
        self.item_repo = item_repo
        self.mov_repo = mov_repo

    def execute(self, dados: RegistrarEntradaDTO) -> Movimentacao:
        item = self.item_repo.get_by_id(dados.item_estoque_id)
        if item is None:
            raise ItemNaoEncontrado()

        # Aggregate creates Movimentacao and mutates saldo internally
        movimentacao = item.registrar_entrada(
            quantidade=dados.quantidade,
            lote=dados.lote,
            motivo=dados.motivo,
        )

        self.item_repo.save(item)
        self.mov_repo.save(movimentacao)

        return movimentacao
