from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.entities.base import BaseEntity
from src.shared.domain.exceptions.base import DomainException
from src.estoque.domain.exceptions.estoque import QuantidadeInvalida
from src.estoque.domain.value_objects.tipo_movimentacao import TipoMovimentacao


@dataclass
class Movimentacao(BaseEntity):
    item_estoque_id: UUID | None = None
    tipo: TipoMovimentacao | None = None
    quantidade: int = 0
    lote: str | None = None
    motivo: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.item_estoque_id is None:
            raise DomainException(
                "ESTOQUE_MOVIMENTACAO_ITEM_OBRIGATORIO",
                "Item de estoque e obrigatorio",
            )
        if self.tipo is None:
            raise DomainException(
                "ESTOQUE_MOVIMENTACAO_TIPO_OBRIGATORIO",
                "Tipo de movimentacao e obrigatorio",
            )
        if self.quantidade <= 0:
            raise QuantidadeInvalida()
