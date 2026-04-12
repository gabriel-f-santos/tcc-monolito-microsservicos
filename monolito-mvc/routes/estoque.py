"""Estoque routes — entrada, saida, consultas, movimentacoes."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from models import ItemEstoque, Movimentacao, AlertaEstoque
from schemas import (
    ItemEstoqueResponse, MovimentacaoRequest, MovimentacaoResponse,
    ConfigurarAlertaRequest, AlertaResponse,
)

router = APIRouter(prefix="/api/v1/estoque", tags=["estoque"])


@router.get("", response_model=list[ItemEstoqueResponse])
def listar_itens(session: Session = Depends(get_session)):
    itens = session.execute(select(ItemEstoque)).scalars().all()
    return [ItemEstoqueResponse.model_validate(i) for i in itens]


@router.get("/{item_id}", response_model=ItemEstoqueResponse)
def buscar_item(item_id: uuid.UUID, session: Session = Depends(get_session)):
    item = session.execute(
        select(ItemEstoque).where(ItemEstoque.id == item_id)
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item de estoque nao encontrado")
    return ItemEstoqueResponse.model_validate(item)


@router.get("/produto/{produto_id}", response_model=ItemEstoqueResponse)
def buscar_por_produto(produto_id: uuid.UUID, session: Session = Depends(get_session)):
    item = session.execute(
        select(ItemEstoque).where(ItemEstoque.produto_id == produto_id)
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item de estoque nao encontrado")
    return ItemEstoqueResponse.model_validate(item)


@router.get("/{item_id}/movimentacoes", response_model=list[MovimentacaoResponse])
def listar_movimentacoes(item_id: uuid.UUID, session: Session = Depends(get_session)):
    item = session.execute(
        select(ItemEstoque).where(ItemEstoque.id == item_id)
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item de estoque nao encontrado")
    movs = session.execute(
        select(Movimentacao).where(Movimentacao.item_estoque_id == item_id)
    ).scalars().all()
    return [MovimentacaoResponse.model_validate(m) for m in movs]


@router.post("/{item_id}/entrada", status_code=201, response_model=MovimentacaoResponse)
def registrar_entrada(
    item_id: uuid.UUID,
    body: MovimentacaoRequest,
    session: Session = Depends(get_session),
):
    item = session.execute(
        select(ItemEstoque).where(ItemEstoque.id == item_id)
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item de estoque nao encontrado")

    if not item.ativo:
        raise HTTPException(status_code=422, detail="Item inativo nao aceita entradas")

    item.saldo += body.quantidade
    item.atualizado_em = datetime.now(timezone.utc)

    mov = Movimentacao(
        item_estoque_id=item_id,
        tipo="ENTRADA",
        quantidade=body.quantidade,
        lote=body.lote,
        motivo=body.motivo,
    )
    session.add(mov)
    session.commit()
    session.refresh(mov)
    return MovimentacaoResponse.model_validate(mov)


@router.post("/{item_id}/saida", status_code=201, response_model=MovimentacaoResponse)
def registrar_saida(
    item_id: uuid.UUID,
    body: MovimentacaoRequest,
    session: Session = Depends(get_session),
):
    item = session.execute(
        select(ItemEstoque).where(ItemEstoque.id == item_id)
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item de estoque nao encontrado")

    if item.saldo < body.quantidade:
        raise HTTPException(status_code=422, detail="Estoque insuficiente")

    item.saldo -= body.quantidade
    item.atualizado_em = datetime.now(timezone.utc)

    mov = Movimentacao(
        item_estoque_id=item_id,
        tipo="SAIDA",
        quantidade=body.quantidade,
        lote=body.lote,
        motivo=body.motivo,
    )
    session.add(mov)

    # Alerta de estoque baixo
    if item.estoque_minimo and item.saldo < item.estoque_minimo:
        alerta = AlertaEstoque(
            item_estoque_id=item_id,
            tipo="ESTOQUE_BAIXO",
            saldo_atual=item.saldo,
            estoque_minimo=item.estoque_minimo,
        )
        session.add(alerta)

    session.commit()
    session.refresh(mov)
    return MovimentacaoResponse.model_validate(mov)


@router.patch("/{item_id}/configurar-alerta", response_model=ItemEstoqueResponse)
def configurar_alerta(
    item_id: uuid.UUID,
    body: ConfigurarAlertaRequest,
    session: Session = Depends(get_session),
):
    item = session.execute(
        select(ItemEstoque).where(ItemEstoque.id == item_id)
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item de estoque nao encontrado")

    item.estoque_minimo = body.estoque_minimo
    item.atualizado_em = datetime.now(timezone.utc)
    session.commit()
    session.refresh(item)
    return ItemEstoqueResponse.model_validate(item)


@router.get("/{item_id}/alertas", response_model=list[AlertaResponse])
def listar_alertas(
    item_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    item = session.execute(
        select(ItemEstoque).where(ItemEstoque.id == item_id)
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item de estoque nao encontrado")

    alertas = session.execute(
        select(AlertaEstoque).where(AlertaEstoque.item_estoque_id == item_id)
    ).scalars().all()
    return [AlertaResponse.model_validate(a) for a in alertas]
