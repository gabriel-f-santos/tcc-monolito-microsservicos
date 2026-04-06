from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from src.shared.domain.exceptions.base import DomainException


@dataclass(frozen=True)
class Dinheiro:
    valor: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.valor, Decimal):
            object.__setattr__(self, "valor", Decimal(str(self.valor)))
        quantizado = self.valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if quantizado != self.valor:
            object.__setattr__(self, "valor", quantizado)
        if self.valor <= 0:
            raise DomainException("PRECO_INVALIDO", "Preco deve ser maior que zero")
