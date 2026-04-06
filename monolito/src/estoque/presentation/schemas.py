from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RegistrarEntradaRequest(BaseModel):
    quantidade: int = Field(..., gt=0)
    lote: str | None = None
    motivo: str | None = None


class RegistrarSaidaRequest(BaseModel):
    quantidade: int = Field(..., gt=0)
    motivo: str | None = None


class ItemEstoqueResponse(BaseModel):
    id: UUID
    produto_id: UUID
    sku: str
    nome_produto: str
    categoria_nome: str
    saldo: int
    ativo: bool
    criado_em: datetime

    model_config = {"from_attributes": True}


class MovimentacaoResponse(BaseModel):
    id: UUID
    item_estoque_id: UUID
    tipo: str
    quantidade: int
    lote: str | None
    motivo: str | None
    criado_em: datetime

    model_config = {"from_attributes": True}
