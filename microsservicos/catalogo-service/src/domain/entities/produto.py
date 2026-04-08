from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects.dinheiro import Dinheiro
from src.domain.value_objects.sku import SKU
from src.shared.domain.entities.base import BaseEntity
from src.shared.domain.exceptions.base import DomainException


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
            raise DomainException("PRODUTO_NOME_OBRIGATORIO", "Nome do produto e obrigatorio")
        if len(self.nome) > 200:
            raise DomainException("PRODUTO_NOME_INVALIDO", "Nome deve ter no maximo 200 caracteres")
        if self.descricao and len(self.descricao) > 1000:
            raise DomainException("PRODUTO_DESCRICAO_INVALIDA", "Descricao deve ter no maximo 1000 caracteres")
        if self.preco is None:
            raise DomainException("PRODUTO_PRECO_OBRIGATORIO", "Preco e obrigatorio")
        if self.categoria_id is None:
            raise DomainException("PRODUTO_CATEGORIA_OBRIGATORIA", "Categoria e obrigatoria")

    def atualizar(
        self,
        nome: str | None = None,
        descricao: str | None = None,
        preco: Decimal | None = None,
        categoria_id: UUID | None = None,
    ) -> None:
        """Atualiza campos do produto. Invariantes re-validadas internamente."""
        if nome is not None:
            self.nome = nome
        if descricao is not None:
            self.descricao = descricao
        if preco is not None:
            self.preco = Dinheiro(valor=preco)
        if categoria_id is not None:
            self.categoria_id = categoria_id
        self.atualizado_em = datetime.now(timezone.utc)
        # Re-validate invariants after mutation
        self.__post_init__()

    def desativar(self) -> None:
        """Desativa o produto. Nao pode ser reativado."""
        self.ativo = False
        self.atualizado_em = datetime.now(timezone.utc)
