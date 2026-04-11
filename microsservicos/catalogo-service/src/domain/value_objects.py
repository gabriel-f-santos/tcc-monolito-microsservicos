import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from src.shared.exceptions import DomainException

SKU_PATTERN = re.compile(r"^[A-Za-z0-9-]{3,50}$")


@dataclass(frozen=True)
class SKU:
    valor: str

    def __post_init__(self) -> None:
        if not self.valor or not SKU_PATTERN.match(self.valor):
            raise DomainException(
                "SKU_INVALIDO",
                "SKU deve ser alfanumerico (com hifen), entre 3 e 50 caracteres",
            )


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
