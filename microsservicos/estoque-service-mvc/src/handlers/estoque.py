"""Estoque handler — entrada, saida, consultas, movimentacoes.
Tudo inline (MVC): roteamento + queries DynamoDB no mesmo arquivo.
Em testes usa dicts in-memory; em prod usa boto3 DynamoDB.
"""
import json
import os
import uuid
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Storage — in-memory para testes, DynamoDB para prod
# ---------------------------------------------------------------------------
_USE_DYNAMO = os.environ.get("USE_DYNAMO", "false").lower() == "true"
_ITENS_TABLE = os.environ.get("ITENS_TABLE", "tcc-mvc-estoque-itens")
_MOVS_TABLE = os.environ.get("MOVIMENTACOES_TABLE", "tcc-mvc-estoque-movimentacoes")

# In-memory stores (usado em testes)
_itens: dict[str, dict] = {}
_movimentacoes: dict[str, dict] = {}


def _dynamo_table(name):
    import boto3
    return boto3.resource("dynamodb").Table(name)


# --- CRUD helpers ---

def _get_item(item_id: str) -> dict | None:
    if _USE_DYNAMO:
        resp = _dynamo_table(_ITENS_TABLE).get_item(Key={"id": item_id})
        return resp.get("Item")
    return _itens.get(item_id)


def _get_item_by_produto(produto_id: str) -> dict | None:
    if _USE_DYNAMO:
        table = _dynamo_table(_ITENS_TABLE)
        resp = table.scan(
            FilterExpression="produto_id = :pid",
            ExpressionAttributeValues={":pid": produto_id},
        )
        items = resp.get("Items", [])
        return items[0] if items else None
    for item in _itens.values():
        if item["produto_id"] == produto_id:
            return item
    return None


def _list_itens() -> list[dict]:
    if _USE_DYNAMO:
        return _dynamo_table(_ITENS_TABLE).scan().get("Items", [])
    return list(_itens.values())


def _put_item(item: dict):
    if _USE_DYNAMO:
        _dynamo_table(_ITENS_TABLE).put_item(Item=item)
    else:
        _itens[item["id"]] = item


def _put_mov(mov: dict):
    if _USE_DYNAMO:
        _dynamo_table(_MOVS_TABLE).put_item(Item=mov)
    else:
        _movimentacoes[mov["id"]] = mov


def _list_movs(item_id: str) -> list[dict]:
    if _USE_DYNAMO:
        table = _dynamo_table(_MOVS_TABLE)
        resp = table.scan(
            FilterExpression="item_estoque_id = :iid",
            ExpressionAttributeValues={":iid": item_id},
        )
        return resp.get("Items", [])
    return [m for m in _movimentacoes.values() if m["item_estoque_id"] == item_id]


# ---------------------------------------------------------------------------
# Respostas HTTP
# ---------------------------------------------------------------------------

def _resp(status: int, body=None):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body) if body is not None else "",
    }


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def handler(event, context):
    method = event.get("httpMethod", "")
    path = event.get("path", "")
    body = json.loads(event["body"]) if event.get("body") else {}

    # POST /api/v1/estoque/{id}/entrada
    if method == "POST" and "/entrada" in path:
        item_id = path.replace("/api/v1/estoque/", "").replace("/entrada", "")
        return _registrar_entrada(item_id, body)

    # POST /api/v1/estoque/{id}/saida
    if method == "POST" and "/saida" in path:
        item_id = path.replace("/api/v1/estoque/", "").replace("/saida", "")
        return _registrar_saida(item_id, body)

    # GET /api/v1/estoque/produto/{produto_id}
    if method == "GET" and "/produto/" in path:
        produto_id = path.split("/produto/")[-1]
        return _buscar_por_produto(produto_id)

    # GET /api/v1/estoque/{id}/movimentacoes
    if method == "GET" and "/movimentacoes" in path:
        item_id = path.replace("/api/v1/estoque/", "").replace("/movimentacoes", "")
        return _listar_movimentacoes(item_id)

    # GET /api/v1/estoque/{id}
    if method == "GET" and path != "/api/v1/estoque":
        item_id = path.replace("/api/v1/estoque/", "")
        return _buscar_item(item_id)

    # GET /api/v1/estoque
    if method == "GET":
        return _listar_itens()

    return _resp(405, {"message": "Method not allowed"})


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def _listar_itens():
    itens = _list_itens()
    return _resp(200, itens)


def _buscar_item(item_id: str):
    item = _get_item(item_id)
    if not item:
        return _resp(404, {"detail": "Item de estoque nao encontrado"})
    return _resp(200, item)


def _buscar_por_produto(produto_id: str):
    item = _get_item_by_produto(produto_id)
    if not item:
        return _resp(404, {"detail": "Item de estoque nao encontrado"})
    return _resp(200, item)


def _listar_movimentacoes(item_id: str):
    item = _get_item(item_id)
    if not item:
        return _resp(404, {"detail": "Item de estoque nao encontrado"})
    movs = _list_movs(item_id)
    return _resp(200, movs)


def _registrar_entrada(item_id: str, body: dict):
    item = _get_item(item_id)
    if not item:
        return _resp(404, {"detail": "Item de estoque nao encontrado"})

    quantidade = body.get("quantidade", 0)
    if quantidade <= 0:
        return _resp(422, {"detail": "Quantidade deve ser maior que zero"})

    item["saldo"] = item.get("saldo", 0) + quantidade
    item["atualizado_em"] = datetime.now(timezone.utc).isoformat()
    _put_item(item)

    mov = {
        "id": str(uuid.uuid4()),
        "item_estoque_id": item_id,
        "tipo": "ENTRADA",
        "quantidade": quantidade,
        "lote": body.get("lote"),
        "motivo": body.get("motivo"),
        "criado_em": datetime.now(timezone.utc).isoformat(),
    }
    _put_mov(mov)
    return _resp(201, mov)


def _registrar_saida(item_id: str, body: dict):
    item = _get_item(item_id)
    if not item:
        return _resp(404, {"detail": "Item de estoque nao encontrado"})

    quantidade = body.get("quantidade", 0)
    if quantidade <= 0:
        return _resp(422, {"detail": "Quantidade deve ser maior que zero"})

    if item.get("saldo", 0) < quantidade:
        return _resp(422, {"detail": "Estoque insuficiente"})

    item["saldo"] = item["saldo"] - quantidade
    item["atualizado_em"] = datetime.now(timezone.utc).isoformat()
    _put_item(item)

    mov = {
        "id": str(uuid.uuid4()),
        "item_estoque_id": item_id,
        "tipo": "SAIDA",
        "quantidade": quantidade,
        "lote": body.get("lote"),
        "motivo": body.get("motivo"),
        "criado_em": datetime.now(timezone.utc).isoformat(),
    }
    _put_mov(mov)
    return _resp(201, mov)
