"""Categorias routes — CRUD inline."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from models import Categoria
from schemas import CategoriaResponse, CriarCategoriaRequest

router = APIRouter(prefix="/api/v1/categorias", tags=["categorias"])


@router.post("", status_code=201, response_model=CategoriaResponse)
def criar_categoria(body: CriarCategoriaRequest, session: Session = Depends(get_session)):
    existente = session.execute(
        select(Categoria).where(Categoria.nome == body.nome)
    ).scalar_one_or_none()
    if existente:
        raise HTTPException(status_code=409, detail="Categoria ja existe")

    categoria = Categoria(nome=body.nome, descricao=body.descricao)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return CategoriaResponse.model_validate(categoria)


@router.get("", response_model=list[CategoriaResponse])
def listar_categorias(session: Session = Depends(get_session)):
    categorias = session.execute(select(Categoria)).scalars().all()
    return [CategoriaResponse.model_validate(c) for c in categorias]


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def buscar_categoria(categoria_id: uuid.UUID, session: Session = Depends(get_session)):
    categoria = session.execute(
        select(Categoria).where(Categoria.id == categoria_id)
    ).scalar_one_or_none()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada")
    return CategoriaResponse.model_validate(categoria)
