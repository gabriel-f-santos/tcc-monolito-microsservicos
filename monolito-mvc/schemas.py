"""Pydantic schemas — request/response DTOs."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# --- Auth ---

class RegistrarRequest(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    senha: str = Field(..., min_length=8)


class UsuarioResponse(BaseModel):
    id: UUID
    nome: str
    email: str
    criado_em: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Categorias ---

class CriarCategoriaRequest(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = None


class CategoriaResponse(BaseModel):
    id: UUID
    nome: str
    descricao: Optional[str] = None
    criado_em: datetime

    model_config = {"from_attributes": True}


# --- Produtos ---

class CriarProdutoRequest(BaseModel):
    sku: str = Field(..., min_length=3, max_length=50)
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = None
    preco: float = Field(..., gt=0)
    categoria_id: UUID


class AtualizarProdutoRequest(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = None
    preco: Optional[float] = Field(None, gt=0)


class CategoriaEmProdutoResponse(BaseModel):
    id: UUID
    nome: str

    model_config = {"from_attributes": True}


class ProdutoResponse(BaseModel):
    id: UUID
    sku: str
    nome: str
    descricao: Optional[str] = None
    preco: float
    ativo: bool
    categoria: CategoriaEmProdutoResponse
    criado_em: datetime

    model_config = {"from_attributes": True}


# --- Estoque ---

class MovimentacaoRequest(BaseModel):
    quantidade: int = Field(..., gt=0)
    lote: Optional[str] = None
    motivo: Optional[str] = None


class MovimentacaoResponse(BaseModel):
    id: UUID
    item_estoque_id: UUID
    tipo: str
    quantidade: int
    lote: Optional[str] = None
    motivo: Optional[str] = None
    criado_em: datetime

    model_config = {"from_attributes": True}


class ItemEstoqueResponse(BaseModel):
    id: UUID
    produto_id: UUID
    sku: str
    nome_produto: str
    categoria_nome: str
    saldo: int
    ativo: bool
    estoque_minimo: int = 0
    criado_em: datetime

    model_config = {"from_attributes": True}


class ConfigurarAlertaRequest(BaseModel):
    estoque_minimo: int = Field(..., ge=0)


class AlertaResponse(BaseModel):
    id: UUID
    item_estoque_id: UUID
    tipo: str
    saldo_atual: int
    estoque_minimo: int
    criado_em: datetime

    model_config = {"from_attributes": True}
