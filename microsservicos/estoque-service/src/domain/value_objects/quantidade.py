from dataclasses import dataclass

from src.shared.domain.exceptions.base import DomainException


@dataclass(frozen=True)
class Quantidade:
    valor: int

    def __post_init__(self) -> None:
        if self.valor <= 0:
            raise DomainException(
                "QUANTIDADE_INVALIDA", "Quantidade deve ser maior que zero"
            )
