from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.entities.base import BaseEntity
from src.shared.domain.exceptions.base import DomainException


@dataclass
class AlertaEstoque(BaseEntity):
    item_estoque_id: UUID | None = None
    tipo: str = "ESTOQUE_BAIXO"
    saldo_atual: int = 0
    estoque_minimo: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.item_estoque_id is None:
            raise DomainException(
                "ALERTA_ITEM_OBRIGATORIO",
                "Item de estoque e obrigatorio",
            )
        if self.tipo != "ESTOQUE_BAIXO":
            raise DomainException(
                "ALERTA_TIPO_INVALIDO",
                "Tipo de alerta invalido",
            )
