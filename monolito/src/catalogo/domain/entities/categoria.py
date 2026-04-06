from dataclasses import dataclass

from src.shared.domain.entities.base import BaseEntity
from src.shared.domain.exceptions.base import DomainException


@dataclass
class Categoria(BaseEntity):
    nome: str = ""
    descricao: str = ""

    def __post_init__(self):
        if not self.nome or not self.nome.strip():
            raise DomainException("NOME_OBRIGATORIO", "Nome e obrigatorio")
        if len(self.nome) > 100:
            raise DomainException("NOME_INVALIDO", "Nome deve ter no maximo 100 caracteres")
