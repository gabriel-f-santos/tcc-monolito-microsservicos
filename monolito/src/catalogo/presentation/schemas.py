from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CriarCategoriaRequest(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: str = ""


class CategoriaResponse(BaseModel):
    id: UUID
    nome: str
    descricao: str
    criado_em: datetime

    model_config = {"from_attributes": True}


class CategoriaNested(BaseModel):
    id: UUID
    nome: str


class CriarProdutoRequest(BaseModel):
    sku: str = Field(..., min_length=3, max_length=50)
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: str | None = None
    preco: Decimal = Field(..., gt=0)
    categoria_id: UUID


class AtualizarProdutoRequest(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=200)
    descricao: str | None = None
    preco: Decimal | None = Field(None, gt=0)


class ProdutoResponse(BaseModel):
    id: UUID
    sku: str
    nome: str
    descricao: str | None
    preco: Decimal
    categoria: CategoriaNested
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
