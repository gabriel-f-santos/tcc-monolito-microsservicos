"""Event consumer — consome eventos do catalogo via SQS (wrapper SNS).

Eventos suportados:
  - ProdutoCriado     -> cria ItemEstoque (saldo=0), idempotente por produto_id
  - ProdutoAtualizado -> atualiza projecao local (nome, categoria)
  - ProdutoDesativado -> marca ativo=false
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone

import boto3


def _itens_table():
    return boto3.resource("dynamodb", region_name="us-east-1").Table(
        os.environ["ITENS_ESTOQUE_TABLE"]
    )


def _find_by_produto(produto_id: str):
    resp = _itens_table().scan()
    for it in resp.get("Items", []):
        if it.get("produto_id") == produto_id:
            return it
    return None


def _handle_produto_criado(dados: dict) -> None:
    produto_id = dados.get("produto_id")
    if not produto_id:
        return
    # Idempotencia: se ja existe item para esse produto_id, nao cria outro
    if _find_by_produto(produto_id) is not None:
        return

    now = datetime.now(timezone.utc).isoformat()
    item = {
        "id": str(uuid.uuid4()),
        "produto_id": produto_id,
        "sku": dados.get("sku"),
        "nome_produto": dados.get("nome"),
        "categoria_nome": dados.get("categoria_nome"),
        "saldo": 0,
        "ativo": True,
        "criado_em": now,
        "atualizado_em": now,
    }
    _itens_table().put_item(Item=item)


def _handle_produto_atualizado(dados: dict) -> None:
    produto_id = dados.get("produto_id")
    if not produto_id:
        return
    existente = _find_by_produto(produto_id)
    if existente is None:
        return
    now = datetime.now(timezone.utc).isoformat()
    _itens_table().update_item(
        Key={"id": existente["id"]},
        UpdateExpression=(
            "SET nome_produto = :n, categoria_nome = :c, sku = :s, atualizado_em = :a"
        ),
        ExpressionAttributeValues={
            ":n": dados.get("nome", existente.get("nome_produto")),
            ":c": dados.get("categoria_nome", existente.get("categoria_nome")),
            ":s": dados.get("sku", existente.get("sku")),
            ":a": now,
        },
    )


def _handle_produto_desativado(dados: dict) -> None:
    produto_id = dados.get("produto_id")
    if not produto_id:
        return
    existente = _find_by_produto(produto_id)
    if existente is None:
        return
    now = datetime.now(timezone.utc).isoformat()
    _itens_table().update_item(
        Key={"id": existente["id"]},
        UpdateExpression="SET ativo = :f, atualizado_em = :a",
        ExpressionAttributeValues={":f": False, ":a": now},
    )


_HANDLERS = {
    "ProdutoCriado": _handle_produto_criado,
    "ProdutoAtualizado": _handle_produto_atualizado,
    "ProdutoDesativado": _handle_produto_desativado,
}


def handler(event, context):
    # Iterar mesmo com BatchSize=1 — Lambda pode entregar N em retries
    for record in event.get("Records", []):
        sqs_body = json.loads(record["body"])        # camada 1: envelope SNS
        message = json.loads(sqs_body["Message"])     # camada 2: payload real
        evento = message.get("evento")
        dados = message.get("dados", {})
        fn = _HANDLERS.get(evento)
        if fn is not None:
            fn(dados)
    return {"statusCode": 200, "body": json.dumps({"processed": True})}
