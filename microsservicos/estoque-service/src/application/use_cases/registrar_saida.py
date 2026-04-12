from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.entities.alerta_estoque import AlertaEstoque
from src.domain.entities.movimentacao import Movimentacao
from src.domain.exceptions.estoque import ItemNaoEncontrado
from src.domain.repositories.alerta_estoque_repository import AlertaEstoqueRepository
from src.domain.repositories.item_estoque_repository import ItemEstoqueRepository
from src.domain.repositories.movimentacao_repository import MovimentacaoRepository


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

        movimentacao = item.registrar_saida(
            quantidade=dados.quantidade,
            motivo=dados.motivo,
        )

        self.item_repo.save(item)
        self.mov_repo.save(movimentacao)

        if (
            self.alerta_repo is not None
            and item.estoque_minimo > 0
            and item.saldo < item.estoque_minimo
        ):
            now = datetime.now(timezone.utc)
            alerta = AlertaEstoque(
                id=uuid4(),
                item_estoque_id=item.id,
                tipo="ESTOQUE_BAIXO",
                saldo_atual=item.saldo,
                estoque_minimo=item.estoque_minimo,
                criado_em=now,
                atualizado_em=now,
            )
            self.alerta_repo.save(alerta)

        return movimentacao
