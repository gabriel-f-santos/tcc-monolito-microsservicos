from dataclasses import dataclass
from uuid import UUID

from src.estoque.domain.entities.movimentacao import Movimentacao
from src.estoque.domain.exceptions.estoque import ItemNaoEncontrado
from src.estoque.domain.repositories.alerta_estoque_repository import AlertaEstoqueRepository
from src.estoque.domain.repositories.item_estoque_repository import ItemEstoqueRepository
from src.estoque.domain.repositories.movimentacao_repository import MovimentacaoRepository


@dataclass
class RegistrarSaidaDTO:
    item_estoque_id: UUID
    quantidade: int
    motivo: str | None = None


class RegistrarSaidaUseCase:
    def __init__(
        self,
        item_repo: ItemEstoqueRepository,
        mov_repo: MovimentacaoRepository,
        alerta_repo: AlertaEstoqueRepository | None = None,
    ) -> None:
        self.item_repo = item_repo
        self.mov_repo = mov_repo
        self.alerta_repo = alerta_repo

    def execute(self, dados: RegistrarSaidaDTO) -> Movimentacao:
        item = self.item_repo.get_by_id(dados.item_estoque_id)
        if item is None:
            raise ItemNaoEncontrado()

        # Aggregate validates saldo >= 0 invariant internally
        movimentacao, alerta = item.registrar_saida(
            quantidade=dados.quantidade,
            motivo=dados.motivo,
        )

        self.item_repo.save(item)
        self.mov_repo.save(movimentacao)

        if alerta is not None and self.alerta_repo is not None:
            self.alerta_repo.save(alerta)

        return movimentacao
