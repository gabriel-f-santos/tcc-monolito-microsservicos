from datetime import datetime
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
