import re
from dataclasses import dataclass

from src.shared.domain.exceptions.base import DomainException

SKU_PATTERN = re.compile(r"^[A-Za-z0-9-]{3,50}$")


@dataclass(frozen=True)
class SKU:
    valor: str

    def __post_init__(self) -> None:
        if not self.valor or not SKU_PATTERN.match(self.valor):
            raise DomainException("SKU_INVALIDO", "SKU deve ser alfanumerico (com hifen), entre 3 e 50 caracteres")
