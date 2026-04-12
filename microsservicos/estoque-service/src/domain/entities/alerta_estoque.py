from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.entities.base import BaseEntity


@dataclass
class AlertaEstoque(BaseEntity):
    item_estoque_id: UUID | None = None
    tipo: str = "ESTOQUE_BAIXO"
    saldo_atual: int = 0
    estoque_minimo: int = 0
