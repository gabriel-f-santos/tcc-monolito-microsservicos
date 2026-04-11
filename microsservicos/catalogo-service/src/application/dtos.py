from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class CriarCategoriaDTO:
    nome: str
    descricao: str | None = None


@dataclass
class CriarProdutoDTO:
    sku: str
    nome: str
    preco: Decimal
    categoria_id: UUID
    descricao: str | None = None


@dataclass
class AtualizarProdutoDTO:
    nome: str | None = None
    descricao: str | None = None
    preco: Decimal | None = None
