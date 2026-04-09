"""Estoque handlers — entrada, saida, consultas com DynamoDB inline."""
import json
import os
import re
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr

ITENS_TABLE = os.environ.get("ITENS_ESTOQUE_TABLE", "tcc-itens-estoque")
MOVS_TABLE = os.environ.get("MOVIMENTACOES_TABLE", "tcc-movimentacoes")

_itens_table = None
_movs_table = None


def _get_itens_table():
    global _itens_table
    if _itens_table is None:
        dynamodb = boto3.resource("dynamodb")
        _itens_table = dynamodb.Table(ITENS_TABLE)
    return _itens_table


def _get_movs_table():
    global _movs_table
    if _movs_table is None:
        dynamodb = boto3.resource("dynamodb")
        _movs_table = dynamodb.Table(MOVS_TABLE)
    return _movs_table


def handler(event, context):
    method = event.get("httpMethod", "")
    path = event.get("path", "")

    # POST /api/v1/estoque/{id}/entrada
    m = re.match(r"^/api/v1/estoque/([^/]+)/entrada$", path)
    if m and method == "POST":
        return _registrar_entrada(m.group(1), event)

    # POST /api/v1/estoque/{id}/saida
    m = re.match(r"^/api/v1/estoque/([^/]+)/saida$", path)
    if m and method == "POST":
        return _registrar_saida(m.group(1), event)

    # GET /api/v1/estoque/{id}/movimentacoes
    m = re.match(r"^/api/v1/estoque/([^/]+)/movimentacoes$", path)
    if m and method == "GET":
        return _listar_movimentacoes(m.group(1))

    # GET /api/v1/estoque/produto/{produto_id}
    m = re.match(r"^/api/v1/estoque/produto/([^/]+)$", path)
    if m and method == "GET":
        return _buscar_por_produto(m.group(1))

    # GET /api/v1/estoque/{id}
    m = re.match(r"^/api/v1/estoque/([^/]+)$", path)
    if m and method == "GET":
        return _buscar_item(m.group(1))

    # GET /api/v1/estoque
    if path == "/api/v1/estoque" and method == "GET":
        return _listar_itens()

    return _response(404, {"detail": "Rota nao encontrada"})


def _registrar_entrada(item_id, event):
    body = json.loads(event.get("body", "{}"))
    quantidade = body.get("quantidade", 0)

    if not isinstance(quantidade, int) or quantidade <= 0:
        return _response(422, {"detail": "Quantidade deve ser maior que zero"})

    table = _get_itens_table()
    result = table.get_item(Key={"id": item_id})
    item = result.get("Item")
    if not item:
        return _response(404, {"detail": "Item de estoque nao encontrado"})

    if not item.get("ativo", True):
        return _response(422, {"detail": "Item inativo nao aceita entradas"})

    agora = datetime.now(timezone.utc).isoformat()
    novo_saldo = int(item.get("saldo", 0)) + quantidade
    table.update_item(
        Key={"id": item_id},
        UpdateExpression="SET saldo = :s, atualizado_em = :a",
        ExpressionAttributeValues={":s": novo_saldo, ":a": agora},
    )

    mov_id = str(uuid.uuid4())
    mov = {
        "id": mov_id,
        "item_estoque_id": item_id,
        "tipo": "ENTRADA",
        "quantidade": quantidade,
        "lote": body.get("lote"),
        "motivo": body.get("motivo"),
        "criado_em": agora,
    }
    _get_movs_table().put_item(Item={k: v for k, v in mov.items() if v is not None})

    return _response(201, mov)


def _registrar_saida(item_id, event):
    body = json.loads(event.get("body", "{}"))
    quantidade = body.get("quantidade", 0)

    if not isinstance(quantidade, int) or quantidade <= 0:
        return _response(422, {"detail": "Quantidade deve ser maior que zero"})

    table = _get_itens_table()
    result = table.get_item(Key={"id": item_id})
    item = result.get("Item")
    if not item:
        return _response(404, {"detail": "Item de estoque nao encontrado"})

    saldo_atual = int(item.get("saldo", 0))
    if saldo_atual < quantidade:
        return _response(422, {"detail": "Estoque insuficiente"})

    agora = datetime.now(timezone.utc).isoformat()
    novo_saldo = saldo_atual - quantidade
    table.update_item(
        Key={"id": item_id},
        UpdateExpression="SET saldo = :s, atualizado_em = :a",
        ExpressionAttributeValues={":s": novo_saldo, ":a": agora},
    )

    mov_id = str(uuid.uuid4())
    mov = {
        "id": mov_id,
        "item_estoque_id": item_id,
        "tipo": "SAIDA",
        "quantidade": quantidade,
        "lote": body.get("lote"),
        "motivo": body.get("motivo"),
        "criado_em": agora,
    }
    _get_movs_table().put_item(Item={k: v for k, v in mov.items() if v is not None})

    return _response(201, mov)


def _listar_itens():
    result = _get_itens_table().scan()
    items = result.get("Items", [])
    return _response(200, items)


def _buscar_item(item_id):
    result = _get_itens_table().get_item(Key={"id": item_id})
    item = result.get("Item")
    if not item:
        return _response(404, {"detail": "Item de estoque nao encontrado"})
    return _response(200, item)


def _buscar_por_produto(produto_id):
    result = _get_itens_table().scan(
        FilterExpression=Attr("produto_id").eq(produto_id)
    )
    items = result.get("Items", [])
    if not items:
        return _response(404, {"detail": "Item de estoque nao encontrado"})
    return _response(200, items[0])


def _listar_movimentacoes(item_id):
    result = _get_itens_table().get_item(Key={"id": item_id})
    if not result.get("Item"):
        return _response(404, {"detail": "Item de estoque nao encontrado"})

    movs_result = _get_movs_table().scan(
        FilterExpression=Attr("item_estoque_id").eq(item_id)
    )
    return _response(200, movs_result.get("Items", []))


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
