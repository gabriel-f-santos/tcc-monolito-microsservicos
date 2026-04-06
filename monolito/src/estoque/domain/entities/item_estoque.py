from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.entities.base import BaseEntity
from src.shared.domain.exceptions.base import DomainException


@dataclass
class ItemEstoque(BaseEntity):
    produto_id: UUID | None = None
    saldo: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.produto_id is None:
            raise DomainException("ITEM_ESTOQUE_PRODUTO_OBRIGATORIO", "Produto e obrigatorio")
        if self.saldo < 0:
            raise DomainException("ESTOQUE_SALDO_NEGATIVO", "Saldo nao pode ser negativo")
