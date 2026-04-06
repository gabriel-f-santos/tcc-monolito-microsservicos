from dataclasses import dataclass

from src.shared.domain.entities.base import BaseEntity
from src.shared.domain.exceptions.base import DomainException


@dataclass
class Usuario(BaseEntity):
    nome: str = ""
    email: str = ""
    senha_hash: str = ""

    def __post_init__(self):
        super().__post_init__() if hasattr(super(), '__post_init__') else None
        if not self.nome or not self.nome.strip():
            raise DomainException("NOME_OBRIGATORIO", "Nome e obrigatorio")
        if not self.email or not self.email.strip():
            raise DomainException("EMAIL_OBRIGATORIO", "Email e obrigatorio")
        if not self.senha_hash:
            raise DomainException("SENHA_OBRIGATORIA", "Senha hash e obrigatoria")
        if len(self.nome) > 200:
            raise DomainException("NOME_INVALIDO", "Nome deve ter no maximo 200 caracteres")
