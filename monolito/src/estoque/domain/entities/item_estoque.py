from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.shared.domain.entities.base import BaseEntity
from src.shared.domain.exceptions.base import DomainException
from src.estoque.domain.entities.alerta_estoque import AlertaEstoque
from src.estoque.domain.entities.movimentacao import Movimentacao
from src.estoque.domain.exceptions.estoque import (
    EstoqueInsuficiente,
    ItemInativo,
    QuantidadeInvalida,
)
from src.estoque.domain.value_objects.tipo_movimentacao import TipoMovimentacao


@dataclass
class ItemEstoque(BaseEntity):
    produto_id: UUID | None = None
    sku: str | None = None
    nome_produto: str | None = None
    categoria_nome: str | None = None
    saldo: int = 0
    ativo: bool = True
    estoque_minimo: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.produto_id is None:
            raise DomainException("ITEM_ESTOQUE_PRODUTO_OBRIGATORIO", "Produto e obrigatorio")
        if self.sku is None:
            raise DomainException("ITEM_ESTOQUE_SKU_OBRIGATORIO", "SKU e obrigatorio")
        if self.nome_produto is None:
            raise DomainException("ITEM_ESTOQUE_NOME_OBRIGATORIO", "Nome do produto e obrigatorio")
        if self.categoria_nome is None:
            raise DomainException("ITEM_ESTOQUE_CATEGORIA_OBRIGATORIO", "Categoria e obrigatoria")
        if self.saldo < 0:
            raise DomainException("ESTOQUE_SALDO_NEGATIVO", "Saldo nao pode ser negativo")

    def registrar_entrada(
        self, quantidade: int, lote: str | None = None, motivo: str | None = None
    ) -> Movimentacao:
        if quantidade <= 0:
            raise QuantidadeInvalida()
        if not self.ativo:
            raise ItemInativo()

        self.saldo += quantidade
        self.atualizado_em = datetime.now(timezone.utc)

        now = datetime.now(timezone.utc)
        return Movimentacao(
            id=uuid4(),
            item_estoque_id=self.id,
            tipo=TipoMovimentacao.ENTRADA,
            quantidade=quantidade,
            lote=lote,
            motivo=motivo,
            criado_em=now,
            atualizado_em=now,
        )

    def registrar_saida(
        self, quantidade: int, motivo: str | None = None
    ) -> tuple[Movimentacao, AlertaEstoque | None]:
        if quantidade <= 0:
            raise QuantidadeInvalida()
        if self.saldo < quantidade:
            raise EstoqueInsuficiente(saldo_atual=self.saldo, solicitado=quantidade)

        self.saldo -= quantidade
        self.atualizado_em = datetime.now(timezone.utc)

        now = datetime.now(timezone.utc)
        movimentacao = Movimentacao(
            id=uuid4(),
            item_estoque_id=self.id,
            tipo=TipoMovimentacao.SAIDA,
            quantidade=quantidade,
            motivo=motivo,
            criado_em=now,
            atualizado_em=now,
        )

        alerta = None
        if self.estoque_minimo > 0 and self.saldo < self.estoque_minimo:
            alerta = AlertaEstoque(
                id=uuid4(),
                item_estoque_id=self.id,
                tipo="ESTOQUE_BAIXO",
                saldo_atual=self.saldo,
                estoque_minimo=self.estoque_minimo,
                criado_em=now,
                atualizado_em=now,
            )

        return movimentacao, alerta
