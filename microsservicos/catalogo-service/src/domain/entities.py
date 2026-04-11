from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects import Dinheiro, SKU
from src.shared.entities import BaseEntity
from src.shared.exceptions import DomainException


@dataclass
class Categoria(BaseEntity):
    nome: str = ""
    descricao: str | None = None

    def __post_init__(self):
        super().__post_init__()
        if not self.nome or not self.nome.strip():
            raise DomainException(
                "CATEGORIA_NOME_OBRIGATORIO", "Nome da categoria e obrigatorio"
            )
        if len(self.nome) > 100:
            raise DomainException(
                "CATEGORIA_NOME_INVALIDO", "Nome deve ter no maximo 100 caracteres"
            )
        if self.descricao and len(self.descricao) > 1000:
            raise DomainException(
                "CATEGORIA_DESCRICAO_INVALIDA",
                "Descricao deve ter no maximo 1000 caracteres",
            )


@dataclass
class Produto(BaseEntity):
    sku: SKU | None = None
    nome: str = ""
    descricao: str | None = None
    preco: Dinheiro | None = None
    categoria_id: UUID | None = None
    ativo: bool = True

    def __post_init__(self) -> None:
        if self.sku is None:
            raise DomainException("PRODUTO_SKU_OBRIGATORIO", "SKU e obrigatorio")
        if not self.nome or not self.nome.strip():
            raise DomainException(
                "PRODUTO_NOME_OBRIGATORIO", "Nome do produto e obrigatorio"
            )
        if len(self.nome) > 200:
            raise DomainException(
                "PRODUTO_NOME_INVALIDO", "Nome deve ter no maximo 200 caracteres"
            )
        if self.descricao and len(self.descricao) > 1000:
            raise DomainException(
                "PRODUTO_DESCRICAO_INVALIDA",
                "Descricao deve ter no maximo 1000 caracteres",
            )
        if self.preco is None:
            raise DomainException("PRODUTO_PRECO_OBRIGATORIO", "Preco e obrigatorio")
        if self.categoria_id is None:
            raise DomainException(
                "PRODUTO_CATEGORIA_OBRIGATORIA", "Categoria e obrigatoria"
            )

    def atualizar(
        self,
        nome: str | None = None,
        descricao: str | None = None,
        preco: Decimal | None = None,
        categoria_id: UUID | None = None,
    ) -> None:
        if nome is not None:
            self.nome = nome
        if descricao is not None:
            self.descricao = descricao
        if preco is not None:
            self.preco = Dinheiro(valor=preco)
        if categoria_id is not None:
            self.categoria_id = categoria_id
        self.atualizado_em = datetime.now(timezone.utc)
        self.__post_init__()

    def desativar(self) -> None:
        self.ativo = False
        self.atualizado_em = datetime.now(timezone.utc)
