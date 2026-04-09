"""Catalogo handler — CRUD categorias e produtos com DynamoDB inline."""
import json
import os
import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3


dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

CATEGORIAS_TABLE = os.environ.get("CATEGORIAS_TABLE", "tcc-categorias")
PRODUTOS_TABLE = os.environ.get("PRODUTOS_TABLE", "tcc-produtos")
EVENTOS_TOPIC_ARN = os.environ.get("EVENTOS_TOPIC_ARN", "")


def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }


def _now():
    return datetime.now(timezone.utc).isoformat()


# --- Categorias ---

def _criar_categoria(body):
    table = dynamodb.Table(CATEGORIAS_TABLE)
    nome = body.get("nome", "").strip()
    if not nome:
        return _resp(422, {"detail": "Nome obrigatorio"})

    # Verificar duplicata por nome
    scan = table.scan(FilterExpression="nome = :n", ExpressionAttributeValues={":n": nome})
    if scan["Items"]:
        return _resp(409, {"detail": "Categoria ja existe"})

    cat_id = str(uuid.uuid4())
    agora = _now()
    item = {
        "id": cat_id,
        "nome": nome,
        "descricao": body.get("descricao"),
        "criado_em": agora,
        "atualizado_em": agora,
    }
    table.put_item(Item=item)
    return _resp(201, item)


def _listar_categorias():
    table = dynamodb.Table(CATEGORIAS_TABLE)
    items = table.scan()["Items"]
    return _resp(200, items)


def _buscar_categoria(cat_id):
    table = dynamodb.Table(CATEGORIAS_TABLE)
    resp = table.get_item(Key={"id": cat_id})
    item = resp.get("Item")
    if not item:
        return _resp(404, {"detail": "Categoria nao encontrada"})
    return _resp(200, item)


# --- Produtos ---

def _criar_produto(body):
    table = dynamodb.Table(PRODUTOS_TABLE)
    cat_table = dynamodb.Table(CATEGORIAS_TABLE)

    sku = body.get("sku", "").strip()
    nome = body.get("nome", "").strip()
    preco = body.get("preco")
    categoria_id = body.get("categoria_id", "")

    if not sku or len(sku) < 3:
        return _resp(422, {"detail": "SKU invalido"})
    if not nome:
        return _resp(422, {"detail": "Nome obrigatorio"})
    if preco is None or preco <= 0:
        return _resp(422, {"detail": "Preco deve ser maior que zero"})

    # Verificar categoria existe
    cat_resp = cat_table.get_item(Key={"id": categoria_id})
    cat = cat_resp.get("Item")
    if not cat:
        return _resp(404, {"detail": "Categoria nao encontrada"})

    # Verificar SKU unico
    scan = table.scan(FilterExpression="sku = :s", ExpressionAttributeValues={":s": sku})
    if scan["Items"]:
        return _resp(409, {"detail": "SKU ja existe"})

    prod_id = str(uuid.uuid4())
    agora = _now()
    item = {
        "id": prod_id,
        "sku": sku,
        "nome": nome,
        "descricao": body.get("descricao"),
        "preco": Decimal(str(preco)),
        "categoria_id": categoria_id,
        "ativo": True,
        "criado_em": agora,
        "atualizado_em": agora,
    }
    table.put_item(Item=item)

    # Publicar evento ProdutoCriado no SNS
    if EVENTOS_TOPIC_ARN:
        sns.publish(
            TopicArn=EVENTOS_TOPIC_ARN,
            Message=json.dumps({
                "evento": "ProdutoCriado",
                "dados": {
                    "produto_id": prod_id,
                    "sku": sku,
                    "nome": nome,
                    "categoria_nome": cat["nome"],
                },
            }),
        )

    # Montar resposta com categoria nested
    resp_item = {**item, "preco": float(item["preco"]), "categoria": {"id": cat["id"], "nome": cat["nome"]}}
    return _resp(201, resp_item)


def _listar_produtos(params):
    table = dynamodb.Table(PRODUTOS_TABLE)
    cat_table = dynamodb.Table(CATEGORIAS_TABLE)

    filter_parts = []
    expr_values = {}

    categoria_id = (params or {}).get("categoria_id")
    ativo = (params or {}).get("ativo")

    if categoria_id:
        filter_parts.append("categoria_id = :cid")
        expr_values[":cid"] = categoria_id
    if ativo is not None:
        filter_parts.append("ativo = :a")
        expr_values[":a"] = ativo.lower() == "true" if isinstance(ativo, str) else bool(ativo)

    kwargs = {}
    if filter_parts:
        kwargs["FilterExpression"] = " AND ".join(filter_parts)
        kwargs["ExpressionAttributeValues"] = expr_values

    items = table.scan(**kwargs)["Items"]

    # Enrich com categoria
    result = []
    for p in items:
        cat_resp = cat_table.get_item(Key={"id": p["categoria_id"]})
        cat = cat_resp.get("Item", {})
        p["preco"] = float(p["preco"]) if isinstance(p["preco"], Decimal) else p["preco"]
        p["categoria"] = {"id": cat.get("id", ""), "nome": cat.get("nome", "")}
        result.append(p)
    return _resp(200, result)


def _buscar_produto(prod_id):
    table = dynamodb.Table(PRODUTOS_TABLE)
    cat_table = dynamodb.Table(CATEGORIAS_TABLE)

    resp = table.get_item(Key={"id": prod_id})
    item = resp.get("Item")
    if not item:
        return _resp(404, {"detail": "Produto nao encontrado"})

    cat_resp = cat_table.get_item(Key={"id": item["categoria_id"]})
    cat = cat_resp.get("Item", {})
    item["preco"] = float(item["preco"]) if isinstance(item["preco"], Decimal) else item["preco"]
    item["categoria"] = {"id": cat.get("id", ""), "nome": cat.get("nome", "")}
    return _resp(200, item)


def _atualizar_produto(prod_id, body):
    table = dynamodb.Table(PRODUTOS_TABLE)
    cat_table = dynamodb.Table(CATEGORIAS_TABLE)

    resp = table.get_item(Key={"id": prod_id})
    item = resp.get("Item")
    if not item:
        return _resp(404, {"detail": "Produto nao encontrado"})

    update_parts = []
    expr_values = {}

    if "nome" in body and body["nome"] is not None:
        update_parts.append("nome = :n")
        expr_values[":n"] = body["nome"]
    if "descricao" in body and body["descricao"] is not None:
        update_parts.append("descricao = :d")
        expr_values[":d"] = body["descricao"]
    if "preco" in body and body["preco"] is not None:
        update_parts.append("preco = :p")
        expr_values[":p"] = Decimal(str(body["preco"]))

    update_parts.append("atualizado_em = :u")
    expr_values[":u"] = _now()

    table.update_item(
        Key={"id": prod_id},
        UpdateExpression="SET " + ", ".join(update_parts),
        ExpressionAttributeValues=expr_values,
    )

    # Buscar atualizado
    updated = table.get_item(Key={"id": prod_id})["Item"]
    cat_resp = cat_table.get_item(Key={"id": updated["categoria_id"]})
    cat = cat_resp.get("Item", {})
    updated["preco"] = float(updated["preco"]) if isinstance(updated["preco"], Decimal) else updated["preco"]
    updated["categoria"] = {"id": cat.get("id", ""), "nome": cat.get("nome", "")}
    return _resp(200, updated)


def _desativar_produto(prod_id):
    table = dynamodb.Table(PRODUTOS_TABLE)
    cat_table = dynamodb.Table(CATEGORIAS_TABLE)

    resp = table.get_item(Key={"id": prod_id})
    item = resp.get("Item")
    if not item:
        return _resp(404, {"detail": "Produto nao encontrado"})

    table.update_item(
        Key={"id": prod_id},
        UpdateExpression="SET ativo = :a, atualizado_em = :u",
        ExpressionAttributeValues={":a": False, ":u": _now()},
    )

    updated = table.get_item(Key={"id": prod_id})["Item"]
    cat_resp = cat_table.get_item(Key={"id": updated["categoria_id"]})
    cat = cat_resp.get("Item", {})
    updated["preco"] = float(updated["preco"]) if isinstance(updated["preco"], Decimal) else updated["preco"]
    updated["categoria"] = {"id": cat.get("id", ""), "nome": cat.get("nome", "")}
    return _resp(200, updated)


# --- Router ---

def _extract_id(path, prefix):
    """Extract ID from path like /api/v1/categorias/{id}."""
    suffix = path[len(prefix):]
    if suffix.startswith("/"):
        suffix = suffix[1:]
    parts = suffix.split("/")
    return parts[0] if parts[0] else None


def handler(event, context):
    method = event["httpMethod"]
    path = event["path"]
    body = json.loads(event.get("body") or "{}") if event.get("body") else {}
    params = event.get("queryStringParameters") or {}

    # Categorias
    if path == "/api/v1/categorias" and method == "POST":
        return _criar_categoria(body)
    if path == "/api/v1/categorias" and method == "GET":
        return _listar_categorias()
    if path.startswith("/api/v1/categorias/") and method == "GET":
        cat_id = _extract_id(path, "/api/v1/categorias")
        return _buscar_categoria(cat_id)

    # Produtos
    if path == "/api/v1/produtos" and method == "POST":
        return _criar_produto(body)
    if path == "/api/v1/produtos" and method == "GET":
        return _listar_produtos(params)
    if re.match(r"^/api/v1/produtos/[^/]+/desativar$", path) and method == "PATCH":
        prod_id = path.split("/")[4]
        return _desativar_produto(prod_id)
    if path.startswith("/api/v1/produtos/") and method == "PUT":
        prod_id = _extract_id(path, "/api/v1/produtos")
        return _atualizar_produto(prod_id, body)
    if path.startswith("/api/v1/produtos/") and method == "GET":
        prod_id = _extract_id(path, "/api/v1/produtos")
        return _buscar_produto(prod_id)

    return _resp(404, {"detail": "Rota nao encontrada"})
