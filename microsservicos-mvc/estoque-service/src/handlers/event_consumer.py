"""Event consumer — consome eventos SQS do Catalogo (ProdutoCriado, ProdutoAtualizado, ProdutoDesativado)."""
import json
import logging
import os
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ITENS_TABLE = os.environ.get("ITENS_ESTOQUE_TABLE", "tcc-itens-estoque")

_table = None


def _get_table():
    global _table
    if _table is None:
        dynamodb = boto3.resource("dynamodb")
        _table = dynamodb.Table(ITENS_TABLE)
    return _table


def handler(event, context):
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        message = json.loads(body.get("Message", "{}"))
        evento = message.get("evento")
        dados = message.get("dados", {})

        logger.info(f"Evento recebido: {evento}")

        if evento == "ProdutoCriado":
            _produto_criado(dados)
        elif evento == "ProdutoAtualizado":
            _produto_atualizado(dados)
        elif evento == "ProdutoDesativado":
            _produto_desativado(dados)

    return {"statusCode": 200}


def _produto_criado(dados):
    table = _get_table()
    produto_id = dados.get("produto_id")

    # Idempotente: se ja existe item com esse produto_id, ignorar
    result = table.scan(FilterExpression=Attr("produto_id").eq(produto_id))
    if result.get("Items"):
        logger.info(f"Item para produto {produto_id} ja existe, ignorando")
        return

    agora = datetime.now(timezone.utc).isoformat()
    item = {
        "id": str(uuid.uuid4()),
        "produto_id": produto_id,
        "sku": dados.get("sku", ""),
        "nome_produto": dados.get("nome", ""),
        "categoria_nome": dados.get("categoria_nome", ""),
        "saldo": 0,
        "ativo": True,
        "criado_em": agora,
        "atualizado_em": agora,
    }
    table.put_item(Item=item)
    logger.info(f"Item de estoque criado para produto {produto_id}")


def _produto_atualizado(dados):
    table = _get_table()
    produto_id = dados.get("produto_id")

    result = table.scan(FilterExpression=Attr("produto_id").eq(produto_id))
    items = result.get("Items", [])
    if not items:
        logger.warning(f"Item para produto {produto_id} nao encontrado para atualizar")
        return

    item = items[0]
    agora = datetime.now(timezone.utc).isoformat()
    table.update_item(
        Key={"id": item["id"]},
        UpdateExpression="SET nome_produto = :n, categoria_nome = :c, atualizado_em = :a",
        ExpressionAttributeValues={
            ":n": dados.get("nome", item.get("nome_produto", "")),
            ":c": dados.get("categoria_nome", item.get("categoria_nome", "")),
            ":a": agora,
        },
    )
    logger.info(f"Projecao atualizada para produto {produto_id}")


def _produto_desativado(dados):
    table = _get_table()
    produto_id = dados.get("produto_id")

    result = table.scan(FilterExpression=Attr("produto_id").eq(produto_id))
    items = result.get("Items", [])
    if not items:
        return

    item = items[0]
    agora = datetime.now(timezone.utc).isoformat()
    table.update_item(
        Key={"id": item["id"]},
        UpdateExpression="SET ativo = :a, atualizado_em = :u",
        ExpressionAttributeValues={":a": False, ":u": agora},
    )
    logger.info(f"Item desativado para produto {produto_id}")
