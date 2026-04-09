"""Produtos routes — CRUD inline + cria item_estoque ao criar produto."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from models import Categoria, ItemEstoque, Produto
from schemas import (
    AtualizarProdutoRequest,
    CategoriaEmProdutoResponse,
    CriarProdutoRequest,
    ProdutoResponse,
)

router = APIRouter(prefix="/api/v1/produtos", tags=["produtos"])


def _build_produto_response(produto: Produto, categoria: Categoria) -> ProdutoResponse:
    return ProdutoResponse(
        id=produto.id,
        sku=produto.sku,
        nome=produto.nome,
        descricao=produto.descricao,
        preco=float(produto.preco),
        ativo=produto.ativo,
        categoria=CategoriaEmProdutoResponse(id=categoria.id, nome=categoria.nome),
        criado_em=produto.criado_em,
    )


@router.post("", status_code=201, response_model=ProdutoResponse)
def criar_produto(body: CriarProdutoRequest, session: Session = Depends(get_session)):
    # Verificar categoria
    categoria = session.execute(
        select(Categoria).where(Categoria.id == body.categoria_id)
    ).scalar_one_or_none()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    # Verificar SKU unico
    existente = session.execute(
        select(Produto).where(Produto.sku == body.sku)
    ).scalar_one_or_none()
    if existente:
        raise HTTPException(status_code=409, detail="SKU ja existe")

    produto = Produto(
        sku=body.sku,
        nome=body.nome,
        descricao=body.descricao,
        preco=body.preco,
        categoria_id=body.categoria_id,
    )
    session.add(produto)
    session.flush()

    # Criar item de estoque com saldo=0
    item_estoque = ItemEstoque(
        produto_id=produto.id,
        sku=produto.sku,
        nome_produto=produto.nome,
        categoria_nome=categoria.nome,
        saldo=0,
    )
    session.add(item_estoque)
    session.commit()
    session.refresh(produto)

    return _build_produto_response(produto, categoria)


@router.get("", response_model=list[ProdutoResponse])
def listar_produtos(
    categoria_id: Optional[uuid.UUID] = Query(None),
    ativo: Optional[bool] = Query(None),
    session: Session = Depends(get_session),
):
    stmt = select(Produto)
    if categoria_id is not None:
        stmt = stmt.where(Produto.categoria_id == categoria_id)
    if ativo is not None:
        stmt = stmt.where(Produto.ativo == ativo)

    produtos = session.execute(stmt).scalars().all()
    result = []
    for p in produtos:
        cat = session.execute(
            select(Categoria).where(Categoria.id == p.categoria_id)
        ).scalar_one()
        result.append(_build_produto_response(p, cat))
    return result


@router.get("/{produto_id}", response_model=ProdutoResponse)
def buscar_produto(produto_id: uuid.UUID, session: Session = Depends(get_session)):
    produto = session.execute(
        select(Produto).where(Produto.id == produto_id)
    ).scalar_one_or_none()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    categoria = session.execute(
        select(Categoria).where(Categoria.id == produto.categoria_id)
    ).scalar_one()
    return _build_produto_response(produto, categoria)


@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: uuid.UUID,
    body: AtualizarProdutoRequest,
    session: Session = Depends(get_session),
):
    produto = session.execute(
        select(Produto).where(Produto.id == produto_id)
    ).scalar_one_or_none()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    if body.nome is not None:
        produto.nome = body.nome
    if body.descricao is not None:
        produto.descricao = body.descricao
    if body.preco is not None:
        produto.preco = body.preco

    session.commit()
    session.refresh(produto)
    categoria = session.execute(
        select(Categoria).where(Categoria.id == produto.categoria_id)
    ).scalar_one()
    return _build_produto_response(produto, categoria)


@router.patch("/{produto_id}/desativar", response_model=ProdutoResponse)
def desativar_produto(produto_id: uuid.UUID, session: Session = Depends(get_session)):
    produto = session.execute(
        select(Produto).where(Produto.id == produto_id)
    ).scalar_one_or_none()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    produto.ativo = False
    session.commit()
    session.refresh(produto)
    categoria = session.execute(
        select(Categoria).where(Categoria.id == produto.categoria_id)
    ).scalar_one()
    return _build_produto_response(produto, categoria)
