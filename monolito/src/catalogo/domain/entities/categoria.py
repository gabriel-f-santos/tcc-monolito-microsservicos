from dataclasses import dataclass

from src.shared.domain.entities.base import BaseEntity
from src.shared.domain.exceptions.base import DomainException


@dataclass
class Categoria(BaseEntity):
    nome: str = ""
    descricao: str | None = None

    def __post_init__(self):
        super().__post_init__()
        if not self.nome or not self.nome.strip():
            raise DomainException("CATEGORIA_NOME_OBRIGATORIO", "Nome da categoria e obrigatorio")
        if len(self.nome) > 100:
            raise DomainException("CATEGORIA_NOME_INVALIDO", "Nome deve ter no maximo 100 caracteres")
        if self.descricao and len(self.descricao) > 1000:
            raise DomainException("CATEGORIA_DESCRICAO_INVALIDA", "Descricao deve ter no maximo 1000 caracteres")
