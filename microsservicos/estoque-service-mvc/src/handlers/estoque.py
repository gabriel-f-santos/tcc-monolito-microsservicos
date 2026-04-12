"""Estoque handler — roteamento por method+path com queries DynamoDB inline."""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone

import boto3


def _json(status: int, body) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }


def _itens_table():
    return boto3.resource("dynamodb", region_name="us-east-1").Table(
        os.environ["ITENS_ESTOQUE_TABLE"]
    )


def _movs_table():
    return boto3.resource("dynamodb", region_name="us-east-1").Table(
        os.environ["MOVIMENTACOES_TABLE"]
    )


def _alertas_table():
    return boto3.resource("dynamodb", region_name="us-east-1").Table(
        os.environ["ALERTAS_TABLE"]
    )


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


def _get_item(item_id: str):
    resp = _itens_table().get_item(Key={"id": item_id})
    return resp.get("Item")


def _find_by_produto(produto_id: str):
    resp = _itens_table().scan()
    for it in resp.get("Items", []):
        if it.get("produto_id") == produto_id:
            return it
    return None


def _serialize_item(item: dict) -> dict:
    return {
        "id": item["id"],
        "produto_id": item.get("produto_id"),
        "sku": item.get("sku"),
        "nome_produto": item.get("nome_produto"),
        "categoria_nome": item.get("categoria_nome"),
        "saldo": int(item.get("saldo", 0)),
        "estoque_minimo": int(item.get("estoque_minimo", 0)),
        "ativo": bool(item.get("ativo", True)),
        "criado_em": item.get("criado_em"),
        "atualizado_em": item.get("atualizado_em"),
    }


def _serialize_mov(mov: dict) -> dict:
    return {
        "id": mov["id"],
        "item_estoque_id": mov.get("item_estoque_id"),
        "tipo": mov.get("tipo"),
        "quantidade": int(mov.get("quantidade", 0)),
        "lote": mov.get("lote"),
        "motivo": mov.get("motivo"),
        "criado_em": mov.get("criado_em"),
    }


def _listar_itens():
    resp = _itens_table().scan()
    return _json(200, [_serialize_item(i) for i in resp.get("Items", [])])


def _buscar_item(item_id: str):
    item = _get_item(item_id)
    if not item:
        return _json(404, {"detail": "Item de estoque nao encontrado"})
    return _json(200, _serialize_item(item))


def _buscar_por_produto(produto_id: str):
    item = _find_by_produto(produto_id)
    if not item:
        return _json(404, {"detail": "Item de estoque nao encontrado"})
    return _json(200, _serialize_item(item))


def _listar_movimentacoes(item_id: str):
    item = _get_item(item_id)
    if not item:
        return _json(404, {"detail": "Item de estoque nao encontrado"})
    resp = _movs_table().scan()
    movs = [m for m in resp.get("Items", []) if m.get("item_estoque_id") == item_id]
    return _json(200, [_serialize_mov(m) for m in movs])


def _registrar_entrada(item_id: str, body: dict):
    quantidade = body.get("quantidade")
    if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
        return _json(422, {"detail": "Quantidade deve ser maior que zero"})

    item = _get_item(item_id)
    if not item:
        return _json(404, {"detail": "Item de estoque nao encontrado"})
    if not bool(item.get("ativo", True)):
        return _json(422, {"detail": "Item inativo nao aceita entradas"})

    novo_saldo = int(item.get("saldo", 0)) + quantidade
    now = datetime.now(timezone.utc).isoformat()
    _itens_table().update_item(
        Key={"id": item_id},
        UpdateExpression="SET saldo = :s, atualizado_em = :a",
        ExpressionAttributeValues={":s": novo_saldo, ":a": now},
    )

    mov = {
        "id": str(uuid.uuid4()),
        "item_estoque_id": item_id,
        "tipo": "ENTRADA",
        "quantidade": quantidade,
        "lote": body.get("lote"),
        "motivo": body.get("motivo"),
        "criado_em": now,
    }
    _movs_table().put_item(Item=mov)
    return _json(201, _serialize_mov(mov))


def _registrar_saida(item_id: str, body: dict):
    quantidade = body.get("quantidade")
    if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
        return _json(422, {"detail": "Quantidade deve ser maior que zero"})

    item = _get_item(item_id)
    if not item:
        return _json(404, {"detail": "Item de estoque nao encontrado"})

    saldo_atual = int(item.get("saldo", 0))
    if saldo_atual < quantidade:
        return _json(422, {"detail": "Estoque insuficiente"})

    novo_saldo = saldo_atual - quantidade
    now = datetime.now(timezone.utc).isoformat()
    _itens_table().update_item(
        Key={"id": item_id},
        UpdateExpression="SET saldo = :s, atualizado_em = :a",
        ExpressionAttributeValues={":s": novo_saldo, ":a": now},
    )

    mov = {
        "id": str(uuid.uuid4()),
        "item_estoque_id": item_id,
        "tipo": "SAIDA",
        "quantidade": quantidade,
        "lote": body.get("lote"),
        "motivo": body.get("motivo"),
        "criado_em": now,
    }
    _movs_table().put_item(Item=mov)

    # Alerta de estoque baixo
    estoque_minimo = int(item.get("estoque_minimo", 0))
    if estoque_minimo > 0 and novo_saldo < estoque_minimo:
        alerta = {
            "id": str(uuid.uuid4()),
            "item_estoque_id": item_id,
            "tipo": "ESTOQUE_BAIXO",
            "saldo_atual": novo_saldo,
            "estoque_minimo": estoque_minimo,
            "criado_em": now,
        }
        _alertas_table().put_item(Item=alerta)

    return _json(201, _serialize_mov(mov))


def _configurar_alerta(item_id: str, body: dict):
    estoque_minimo = body.get("estoque_minimo")
    if not isinstance(estoque_minimo, int) or isinstance(estoque_minimo, bool) or estoque_minimo < 0:
        return _json(422, {"detail": "estoque_minimo deve ser >= 0"})

    item = _get_item(item_id)
    if not item:
        return _json(404, {"detail": "Item de estoque nao encontrado"})

    now = datetime.now(timezone.utc).isoformat()
    _itens_table().update_item(
        Key={"id": item_id},
        UpdateExpression="SET estoque_minimo = :m, atualizado_em = :a",
        ExpressionAttributeValues={":m": estoque_minimo, ":a": now},
    )
    item["estoque_minimo"] = estoque_minimo
    item["atualizado_em"] = now
    return _json(200, _serialize_item(item))


def _listar_alertas(item_id: str):
    item = _get_item(item_id)
    if not item:
        return _json(404, {"detail": "Item de estoque nao encontrado"})

    resp = _alertas_table().scan()
    alertas = [a for a in resp.get("Items", []) if a.get("item_estoque_id") == item_id]
    result = []
    for a in alertas:
        result.append({
            "id": a["id"],
            "item_estoque_id": a["item_estoque_id"],
            "tipo": a["tipo"],
            "saldo_atual": int(a["saldo_atual"]),
            "estoque_minimo": int(a["estoque_minimo"]),
            "criado_em": a["criado_em"],
        })
    return _json(200, result)


# --- Roteamento ---------------------------------------------------------------

_RE_BY_PRODUTO = re.compile(r"^/api/v1/estoque/produto/(?P<pid>[^/]+)/?$")
_RE_ENTRADA = re.compile(r"^/api/v1/estoque/(?P<id>[^/]+)/entrada/?$")
_RE_SAIDA = re.compile(r"^/api/v1/estoque/(?P<id>[^/]+)/saida/?$")
_RE_MOVS = re.compile(r"^/api/v1/estoque/(?P<id>[^/]+)/movimentacoes/?$")
_RE_CONF_ALERTA = re.compile(r"^/api/v1/estoque/(?P<id>[^/]+)/configurar-alerta/?$")
_RE_ALERTAS = re.compile(r"^/api/v1/estoque/(?P<id>[^/]+)/alertas/?$")
_RE_BY_ID = re.compile(r"^/api/v1/estoque/(?P<id>[^/]+)/?$")
_RE_LISTAR = re.compile(r"^/api/v1/estoque/?$")


def handler(event, context):
    method = event.get("httpMethod", "GET").upper()
    path = event.get("path", "")

    if method == "GET":
        if _RE_LISTAR.match(path):
            return _listar_itens()
        m = _RE_BY_PRODUTO.match(path)
        if m:
            return _buscar_por_produto(m.group("pid"))
        m = _RE_MOVS.match(path)
        if m:
            return _listar_movimentacoes(m.group("id"))
        m = _RE_ALERTAS.match(path)
        if m:
            return _listar_alertas(m.group("id"))
        m = _RE_BY_ID.match(path)
        if m:
            return _buscar_item(m.group("id"))

    if method == "POST":
        body = _parse_body(event)
        m = _RE_ENTRADA.match(path)
        if m:
            return _registrar_entrada(m.group("id"), body)
        m = _RE_SAIDA.match(path)
        if m:
            return _registrar_saida(m.group("id"), body)

    if method == "PATCH":
        body = _parse_body(event)
        m = _RE_CONF_ALERTA.match(path)
        if m:
            return _configurar_alerta(m.group("id"), body)

    return _json(404, {"detail": "Rota nao encontrada"})
