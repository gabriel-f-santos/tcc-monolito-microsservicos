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


class ConfigurarAlertaRequest(BaseModel):
    estoque_minimo: int = Field(..., ge=0)


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


class MovimentacaoResponse(BaseModel):
    id: UUID
    item_estoque_id: UUID
    tipo: str
    quantidade: int
    lote: str | None
    motivo: str | None
    criado_em: datetime

    model_config = {"from_attributes": True}


class AlertaEstoqueResponse(BaseModel):
    id: UUID
    item_estoque_id: UUID
    tipo: str
    saldo_atual: int
    estoque_minimo: int
    criado_em: datetime

    model_config = {"from_attributes": True}
