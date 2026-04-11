"""Catalogo handler — Categorias + Produtos CRUD inline (MVC).
Uses in-memory dicts for local/test, DynamoDB when env vars are set.
Publishes ProdutoCriado to SNS on product creation.
"""
import json
import os
import re
import uuid
from datetime import datetime, timezone

# --- Storage -----------------------------------------------------------------
# In-memory for tests; DynamoDB for production (when env vars present).

_categorias: dict[str, dict] = {}
_produtos: dict[str, dict] = {}

_USE_DYNAMO = bool(os.environ.get("CATEGORIAS_TABLE"))

if _USE_DYNAMO:
    import boto3
    _dynamo = boto3.resource("dynamodb")
    _cat_table = _dynamo.Table(os.environ["CATEGORIAS_TABLE"])
    _prod_table = _dynamo.Table(os.environ["PRODUTOS_TABLE"])
    _sns = boto3.client("sns")
    _topic_arn = os.environ.get("EVENTOS_TOPIC_ARN", "")


# --- Helpers -----------------------------------------------------------------

def _resp(status: int, body=None):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body) if body is not None else "",
    }


def _parse_body(event):
    raw = event.get("body")
    if raw:
        return json.loads(raw)
    return {}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _extract_id(path: str, prefix: str) -> str | None:
    """Extract resource ID from path like /api/v1/categorias/{id}."""
    pattern = rf"^{re.escape(prefix)}/([^/]+)$"
    m = re.match(pattern, path)
    return m.group(1) if m else None


# --- Categoria storage -------------------------------------------------------

def _cat_put(item: dict):
    if _USE_DYNAMO:
        _cat_table.put_item(Item=item)
    else:
        _categorias[item["id"]] = item


def _cat_get(cat_id: str) -> dict | None:
    if _USE_DYNAMO:
        resp = _cat_table.get_item(Key={"id": cat_id})
        return resp.get("Item")
    return _categorias.get(cat_id)


def _cat_scan() -> list[dict]:
    if _USE_DYNAMO:
        return _cat_table.scan().get("Items", [])
    return list(_categorias.values())


def _cat_find_by_nome(nome: str) -> dict | None:
    for c in _cat_scan():
        if c["nome"] == nome:
            return c
    return None


# --- Produto storage ---------------------------------------------------------

def _prod_put(item: dict):
    if _USE_DYNAMO:
        _prod_table.put_item(Item=item)
    else:
        _produtos[item["id"]] = item


def _prod_get(prod_id: str) -> dict | None:
    if _USE_DYNAMO:
        resp = _prod_table.get_item(Key={"id": prod_id})
        return resp.get("Item")
    return _produtos.get(prod_id)


def _prod_scan() -> list[dict]:
    if _USE_DYNAMO:
        return _prod_table.scan().get("Items", [])
    return list(_produtos.values())


def _prod_find_by_sku(sku: str) -> dict | None:
    for p in _prod_scan():
        if p["sku"] == sku:
            return p
    return None


def _prod_update(prod_id: str, updates: dict):
    item = _prod_get(prod_id)
    if not item:
        return None
    item.update(updates)
    _prod_put(item)
    return item


# --- SNS ---------------------------------------------------------------------

def _publish_produto_criado(produto: dict):
    if not _USE_DYNAMO:
        return
    _sns.publish(
        TopicArn=_topic_arn,
        Subject="ProdutoCriado",
        Message=json.dumps({
            "evento": "ProdutoCriado",
            "produto_id": produto["id"],
            "sku": produto["sku"],
            "nome": produto["nome"],
            "categoria_id": produto["categoria_id"],
        }),
    )


# --- Route handlers ----------------------------------------------------------

def _criar_categoria(event):
    body = _parse_body(event)
    nome = body.get("nome", "").strip()
    if not nome:
        return _resp(422, {"detail": "nome obrigatorio"})

    if _cat_find_by_nome(nome):
        return _resp(409, {"detail": "Categoria ja existe"})

    item = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "descricao": body.get("descricao", ""),
        "criado_em": _now_iso(),
    }
    _cat_put(item)
    return _resp(201, item)


def _listar_categorias():
    return _resp(200, _cat_scan())


def _buscar_categoria(cat_id: str):
    item = _cat_get(cat_id)
    if not item:
        return _resp(404, {"detail": "Categoria nao encontrada"})
    return _resp(200, item)


def _criar_produto(event):
    body = _parse_body(event)
    sku = body.get("sku", "").strip()
    nome = body.get("nome", "").strip()
    preco = body.get("preco")
    categoria_id = body.get("categoria_id", "")

    if not sku or not nome:
        return _resp(422, {"detail": "sku e nome obrigatorios"})
    if preco is None or preco <= 0:
        return _resp(422, {"detail": "preco deve ser maior que zero"})

    cat = _cat_get(categoria_id)
    if not cat:
        return _resp(404, {"detail": "Categoria nao encontrada"})

    if _prod_find_by_sku(sku):
        return _resp(409, {"detail": "SKU ja existe"})

    item = {
        "id": str(uuid.uuid4()),
        "sku": sku,
        "nome": nome,
        "descricao": body.get("descricao", ""),
        "preco": preco,
        "ativo": True,
        "categoria_id": categoria_id,
        "criado_em": _now_iso(),
    }
    _prod_put(item)
    _publish_produto_criado(item)
    return _resp(201, item)


def _listar_produtos(event):
    query = event.get("queryStringParameters") or {}
    items = _prod_scan()
    if "categoria_id" in query:
        items = [p for p in items if p["categoria_id"] == query["categoria_id"]]
    if "ativo" in query:
        ativo_val = query["ativo"].lower() == "true"
        items = [p for p in items if p["ativo"] == ativo_val]
    return _resp(200, items)


def _buscar_produto(prod_id: str):
    item = _prod_get(prod_id)
    if not item:
        return _resp(404, {"detail": "Produto nao encontrado"})
    return _resp(200, item)


def _atualizar_produto(event, prod_id: str):
    item = _prod_get(prod_id)
    if not item:
        return _resp(404, {"detail": "Produto nao encontrado"})

    body = _parse_body(event)
    updates = {}
    if "nome" in body:
        updates["nome"] = body["nome"]
    if "descricao" in body:
        updates["descricao"] = body["descricao"]
    if "preco" in body:
        updates["preco"] = body["preco"]

    updated = _prod_update(prod_id, updates)
    return _resp(200, updated)


def _desativar_produto(prod_id: str):
    item = _prod_get(prod_id)
    if not item:
        return _resp(404, {"detail": "Produto nao encontrado"})

    updated = _prod_update(prod_id, {"ativo": False})
    return _resp(200, updated)


# --- Router ------------------------------------------------------------------

def handler(event, context):
    method = event["httpMethod"]
    path = event["path"]

    # --- Categorias ---
    if path == "/api/v1/categorias":
        if method == "POST":
            return _criar_categoria(event)
        if method == "GET":
            return _listar_categorias()

    cat_id = _extract_id(path, "/api/v1/categorias")
    if cat_id:
        if method == "GET":
            return _buscar_categoria(cat_id)

    # --- Produtos: desativar (must match before generic /{id}) ---
    desat_match = re.match(r"^/api/v1/produtos/([^/]+)/desativar$", path)
    if desat_match:
        if method == "PATCH":
            return _desativar_produto(desat_match.group(1))

    # --- Produtos ---
    if path == "/api/v1/produtos":
        if method == "POST":
            return _criar_produto(event)
        if method == "GET":
            return _listar_produtos(event)

    prod_id = _extract_id(path, "/api/v1/produtos")
    if prod_id:
        if method == "GET":
            return _buscar_produto(prod_id)
        if method == "PUT":
            return _atualizar_produto(event, prod_id)

    return _resp(404, {"detail": "Not found"})
