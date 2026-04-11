from __future__ import annotations

import json
import os
import re
from uuid import UUID

from src.application.use_cases.buscar_item import BuscarItemUseCase
from src.application.use_cases.listar_itens import ListarItensUseCase
from src.application.use_cases.listar_movimentacoes import ListarMovimentacoesUseCase
from src.application.use_cases.registrar_entrada import (
    RegistrarEntradaDTO,
    RegistrarEntradaUseCase,
)
from src.application.use_cases.registrar_saida import (
    RegistrarSaidaDTO,
    RegistrarSaidaUseCase,
)
from src.domain.entities.item_estoque import ItemEstoque
from src.domain.entities.movimentacao import Movimentacao
from src.domain.exceptions.estoque import (
    EstoqueInsuficiente,
    ItemInativo,
    ItemNaoEncontrado,
    QuantidadeInvalida,
)
from src.infrastructure.repositories.dynamodb_item_estoque_repository import (
    DynamoDBItemEstoqueRepository,
)
from src.infrastructure.repositories.dynamodb_movimentacao_repository import (
    DynamoDBMovimentacaoRepository,
)
from src.shared.domain.exceptions.base import DomainException


def _response(status: int, body: dict | list) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }


def _item_repo() -> DynamoDBItemEstoqueRepository:
    return DynamoDBItemEstoqueRepository(os.environ["ITENS_ESTOQUE_TABLE"])


def _mov_repo() -> DynamoDBMovimentacaoRepository:
    return DynamoDBMovimentacaoRepository(os.environ["MOVIMENTACOES_TABLE"])


def _serialize_item(item: ItemEstoque) -> dict:
    return {
        "id": str(item.id),
        "produto_id": str(item.produto_id),
        "sku": item.sku,
        "nome_produto": item.nome_produto,
        "categoria_nome": item.categoria_nome,
        "saldo": int(item.saldo),
        "ativo": bool(item.ativo),
        "criado_em": item.criado_em.isoformat(),
        "atualizado_em": item.atualizado_em.isoformat(),
    }


def _serialize_mov(mov: Movimentacao) -> dict:
    return {
        "id": str(mov.id),
        "item_estoque_id": str(mov.item_estoque_id),
        "tipo": mov.tipo.value,
        "quantidade": int(mov.quantidade),
        "lote": mov.lote,
        "motivo": mov.motivo,
        "criado_em": mov.criado_em.isoformat(),
        "atualizado_em": mov.atualizado_em.isoformat(),
    }


def _parse_body(event: dict) -> dict:
    raw = event.get("body")
    if not raw:
        return {}
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


# Regex de rotas --------------------------------------------------------------
UUID_RE = r"[0-9a-fA-F\-]{36}"
RE_ENTRADA = re.compile(rf"^/api/v1/estoque/(?P<id>{UUID_RE})/entrada$")
RE_SAIDA = re.compile(rf"^/api/v1/estoque/(?P<id>{UUID_RE})/saida$")
RE_MOVS = re.compile(rf"^/api/v1/estoque/(?P<id>{UUID_RE})/movimentacoes$")
RE_POR_PRODUTO = re.compile(rf"^/api/v1/estoque/produto/(?P<pid>{UUID_RE})$")
RE_BY_ID = re.compile(rf"^/api/v1/estoque/(?P<id>{UUID_RE})$")
RE_LIST = re.compile(r"^/api/v1/estoque/?$")


def handler(event, context):
    method = (event.get("httpMethod") or "GET").upper()
    path = event.get("path") or "/"

    try:
        if method == "POST":
            m = RE_ENTRADA.match(path)
            if m:
                return _handle_entrada(UUID(m.group("id")), _parse_body(event))
            m = RE_SAIDA.match(path)
            if m:
                return _handle_saida(UUID(m.group("id")), _parse_body(event))
            return _response(404, {"message": "Rota nao encontrada"})

        if method == "GET":
            m = RE_POR_PRODUTO.match(path)
            if m:
                return _handle_buscar_por_produto(UUID(m.group("pid")))
            m = RE_MOVS.match(path)
            if m:
                return _handle_movimentacoes(UUID(m.group("id")))
            m = RE_BY_ID.match(path)
            if m:
                return _handle_buscar(UUID(m.group("id")))
            if RE_LIST.match(path):
                return _handle_listar(event)
            return _response(404, {"message": "Rota nao encontrada"})

        return _response(405, {"message": "Metodo nao permitido"})

    except ItemNaoEncontrado as exc:
        return _response(404, {"code": exc.code, "message": exc.message})
    except (QuantidadeInvalida, EstoqueInsuficiente, ItemInativo) as exc:
        return _response(422, {"code": exc.code, "message": exc.message})
    except DomainException as exc:
        return _response(422, {"code": exc.code, "message": exc.message})
    except ValueError as exc:
        return _response(422, {"message": str(exc)})


# Handlers concretos ----------------------------------------------------------


def _handle_entrada(item_id: UUID, body: dict) -> dict:
    quantidade = body.get("quantidade")
    if quantidade is None or not isinstance(quantidade, int) or quantidade <= 0:
        raise QuantidadeInvalida()
    uc = RegistrarEntradaUseCase(_item_repo(), _mov_repo())
    mov = uc.execute(
        RegistrarEntradaDTO(
            item_estoque_id=item_id,
            quantidade=quantidade,
            lote=body.get("lote"),
            motivo=body.get("motivo"),
        )
    )
    return _response(201, _serialize_mov(mov))


def _handle_saida(item_id: UUID, body: dict) -> dict:
    quantidade = body.get("quantidade")
    if quantidade is None or not isinstance(quantidade, int) or quantidade <= 0:
        raise QuantidadeInvalida()
    uc = RegistrarSaidaUseCase(_item_repo(), _mov_repo())
    mov = uc.execute(
        RegistrarSaidaDTO(
            item_estoque_id=item_id,
            quantidade=quantidade,
            motivo=body.get("motivo"),
        )
    )
    return _response(201, _serialize_mov(mov))


def _handle_buscar(item_id: UUID) -> dict:
    uc = BuscarItemUseCase(_item_repo())
    item = uc.execute(item_id)
    return _response(200, _serialize_item(item))


def _handle_buscar_por_produto(produto_id: UUID) -> dict:
    uc = BuscarItemUseCase(_item_repo())
    item = uc.execute_por_produto(produto_id)
    return _response(200, _serialize_item(item))


def _handle_listar(event: dict) -> dict:
    query = event.get("queryStringParameters") or {}
    saldo_min = query.get("saldo_min")
    page = int(query.get("page") or 1)
    size = int(query.get("size") or 20)
    uc = ListarItensUseCase(_item_repo())
    itens = uc.execute(
        saldo_min=int(saldo_min) if saldo_min is not None else None,
        page=page,
        size=size,
    )
    return _response(200, [_serialize_item(i) for i in itens])


def _handle_movimentacoes(item_id: UUID) -> dict:
    uc = ListarMovimentacoesUseCase(_item_repo(), _mov_repo())
    movs = uc.execute(item_estoque_id=item_id)
    return _response(200, [_serialize_mov(m) for m in movs])
