"""Catalogo handler (MVC) — roteamento por httpMethod + path, queries inline."""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3


# --- Helpers ------------------------------------------------------------------


def _response(status: int, body) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=_json_default),
    }


def _json_default(value):
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Nao serializavel: {type(value)}")


def _parse_body(event: dict) -> dict:
    raw = event.get("body")
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _categorias_table():
    return boto3.resource("dynamodb").Table(os.environ["CATEGORIAS_TABLE"])


def _produtos_table():
    return boto3.resource("dynamodb").Table(os.environ["PRODUTOS_TABLE"])


def _sns_client():
    return boto3.client("sns")


def _to_decimal(value):
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _produto_to_response(item: dict) -> dict:
    return {
        "id": item["id"],
        "sku": item["sku"],
        "nome": item["nome"],
        "descricao": item.get("descricao"),
        "preco": float(item["preco"]) if isinstance(item.get("preco"), Decimal) else item.get("preco"),
        "ativo": item.get("ativo", True),
        "categoria_id": item.get("categoria_id"),
        "criado_em": item.get("criado_em"),
    }


def _categoria_to_response(item: dict) -> dict:
    return {
        "id": item["id"],
        "nome": item["nome"],
        "descricao": item.get("descricao"),
        "criado_em": item.get("criado_em"),
    }


# --- Categorias ---------------------------------------------------------------


def _criar_categoria(body: dict) -> dict:
    nome = (body.get("nome") or "").strip()
    if not nome:
        return _response(422, {"erro": "nome obrigatorio"})

    table = _categorias_table()
    existentes = table.scan(
        FilterExpression="#n = :nome",
        ExpressionAttributeNames={"#n": "nome"},
        ExpressionAttributeValues={":nome": nome},
    ).get("Items", [])
    if existentes:
        return _response(409, {"erro": "Categoria ja existe"})

    item = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "descricao": body.get("descricao"),
        "criado_em": _now_iso(),
    }
    table.put_item(Item=item)
    return _response(201, _categoria_to_response(item))


def _listar_categorias() -> dict:
    items = _categorias_table().scan().get("Items", [])
    return _response(200, [_categoria_to_response(i) for i in items])


def _buscar_categoria(categoria_id: str) -> dict:
    resp = _categorias_table().get_item(Key={"id": categoria_id})
    item = resp.get("Item")
    if not item:
        return _response(404, {"erro": "Categoria nao encontrada"})
    return _response(200, _categoria_to_response(item))


# --- Produtos -----------------------------------------------------------------


_SKU_RE = re.compile(r"^[A-Za-z0-9\-_]{3,50}$")


def _criar_produto(body: dict) -> dict:
    sku = (body.get("sku") or "").strip()
    nome = (body.get("nome") or "").strip()
    preco_raw = body.get("preco")
    categoria_id = body.get("categoria_id")

    if not sku or not _SKU_RE.match(sku):
        return _response(422, {"erro": "SKU invalido"})
    if not nome:
        return _response(422, {"erro": "nome obrigatorio"})
    if preco_raw is None:
        return _response(422, {"erro": "preco obrigatorio"})
    try:
        preco = _to_decimal(preco_raw)
    except Exception:
        return _response(422, {"erro": "preco invalido"})
    if preco <= 0:
        return _response(422, {"erro": "preco deve ser maior que zero"})
    if not categoria_id:
        return _response(422, {"erro": "categoria_id obrigatorio"})

    # Verificar categoria existe
    cat_resp = _categorias_table().get_item(Key={"id": str(categoria_id)})
    categoria = cat_resp.get("Item")
    if not categoria:
        return _response(404, {"erro": "Categoria nao encontrada"})

    # Verificar SKU unico
    produtos = _produtos_table()
    existentes = produtos.scan(
        FilterExpression="sku = :sku",
        ExpressionAttributeValues={":sku": sku},
    ).get("Items", [])
    if existentes:
        return _response(409, {"erro": "SKU ja existe"})

    item = {
        "id": str(uuid.uuid4()),
        "sku": sku,
        "nome": nome,
        "descricao": body.get("descricao"),
        "preco": preco,
        "ativo": True,
        "categoria_id": str(categoria_id),
        "criado_em": _now_iso(),
    }
    produtos.put_item(Item=item)

    # Publicar evento ProdutoCriado
    _sns_client().publish(
        TopicArn=os.environ["EVENTOS_TOPIC_ARN"],
        Message=json.dumps({
            "evento": "ProdutoCriado",
            "dados": {
                "produto_id": str(item["id"]),
                "sku": sku,
                "nome": nome,
                "categoria_nome": categoria["nome"],
            },
        }),
    )

    return _response(201, _produto_to_response(item))


def _listar_produtos(query: dict | None) -> dict:
    query = query or {}
    items = _produtos_table().scan().get("Items", [])

    categoria_id = query.get("categoria_id")
    if categoria_id:
        items = [i for i in items if i.get("categoria_id") == categoria_id]

    ativo = query.get("ativo")
    if ativo is not None:
        ativo_bool = str(ativo).lower() == "true"
        items = [i for i in items if bool(i.get("ativo")) == ativo_bool]

    return _response(200, [_produto_to_response(i) for i in items])


def _buscar_produto(produto_id: str) -> dict:
    resp = _produtos_table().get_item(Key={"id": produto_id})
    item = resp.get("Item")
    if not item:
        return _response(404, {"erro": "Produto nao encontrado"})
    return _response(200, _produto_to_response(item))


def _atualizar_produto(produto_id: str, body: dict) -> dict:
    table = _produtos_table()
    resp = table.get_item(Key={"id": produto_id})
    item = resp.get("Item")
    if not item:
        return _response(404, {"erro": "Produto nao encontrado"})

    if "nome" in body and body["nome"] is not None:
        item["nome"] = body["nome"]
    if "descricao" in body:
        item["descricao"] = body["descricao"]
    if "preco" in body and body["preco"] is not None:
        try:
            preco = _to_decimal(body["preco"])
        except Exception:
            return _response(422, {"erro": "preco invalido"})
        if preco <= 0:
            return _response(422, {"erro": "preco deve ser maior que zero"})
        item["preco"] = preco

    table.put_item(Item=item)
    return _response(200, _produto_to_response(item))


def _desativar_produto(produto_id: str) -> dict:
    table = _produtos_table()
    resp = table.get_item(Key={"id": produto_id})
    item = resp.get("Item")
    if not item:
        return _response(404, {"erro": "Produto nao encontrado"})
    item["ativo"] = False
    table.put_item(Item=item)
    return _response(200, _produto_to_response(item))


# --- Handler ------------------------------------------------------------------


_CATEGORIA_BY_ID = re.compile(r"^/api/v1/categorias/([^/]+)/?$")
_PRODUTO_BY_ID = re.compile(r"^/api/v1/produtos/([^/]+)/?$")
_PRODUTO_DESATIVAR = re.compile(r"^/api/v1/produtos/([^/]+)/desativar/?$")


def handler(event, context):
    method = (event.get("httpMethod") or "").upper()
    path = event.get("path") or ""
    body = _parse_body(event)
    query = event.get("queryStringParameters") or {}

    # Categorias
    if path == "/api/v1/categorias":
        if method == "POST":
            return _criar_categoria(body)
        if method == "GET":
            return _listar_categorias()
        return _response(405, {"erro": "metodo nao permitido"})

    m = _CATEGORIA_BY_ID.match(path)
    if m:
        categoria_id = m.group(1)
        if method == "GET":
            return _buscar_categoria(categoria_id)
        return _response(405, {"erro": "metodo nao permitido"})

    # Produtos
    if path == "/api/v1/produtos":
        if method == "POST":
            return _criar_produto(body)
        if method == "GET":
            return _listar_produtos(query)
        return _response(405, {"erro": "metodo nao permitido"})

    m = _PRODUTO_DESATIVAR.match(path)
    if m:
        produto_id = m.group(1)
        if method == "PATCH":
            return _desativar_produto(produto_id)
        return _response(405, {"erro": "metodo nao permitido"})

    m = _PRODUTO_BY_ID.match(path)
    if m:
        produto_id = m.group(1)
        if method == "GET":
            return _buscar_produto(produto_id)
        if method == "PUT":
            return _atualizar_produto(produto_id, body)
        return _response(405, {"erro": "metodo nao permitido"})

    return _response(404, {"erro": "rota nao encontrada"})
