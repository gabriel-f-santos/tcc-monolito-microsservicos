"""Event consumer — processa eventos SQS (vindos do SNS).
Consome ProdutoCriado e ProdutoAtualizado para manter projecao local.
"""
import json
import logging
import uuid
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        message = json.loads(body.get("Message", "{}"))
        evento = message.get("evento", "")
        dados = message.get("dados", {})

        logger.info(f"Evento recebido: {evento}")

        if evento == "ProdutoCriado":
            _on_produto_criado(dados)
        elif evento == "ProdutoAtualizado":
            _on_produto_atualizado(dados)
        else:
            logger.warning(f"Evento desconhecido: {evento}")

    return {"statusCode": 200}


def _on_produto_criado(dados: dict):
    """Cria ItemEstoque com saldo=0 a partir do evento ProdutoCriado."""
    from src.handlers.estoque import _get_item_by_produto, _put_item

    produto_id = dados.get("produto_id")
    if not produto_id:
        logger.error("ProdutoCriado sem produto_id")
        return

    # Idempotencia: se ja existe, nao cria de novo
    existing = _get_item_by_produto(produto_id)
    if existing:
        logger.info(f"ItemEstoque ja existe para produto {produto_id}")
        return

    item = {
        "id": str(uuid.uuid4()),
        "produto_id": produto_id,
        "sku": dados.get("sku", ""),
        "nome_produto": dados.get("nome", ""),
        "categoria_nome": dados.get("categoria_nome", ""),
        "saldo": 0,
        "ativo": True,
        "criado_em": datetime.now(timezone.utc).isoformat(),
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }
    _put_item(item)
    logger.info(f"ItemEstoque criado: {item['id']} para produto {produto_id}")


def _on_produto_atualizado(dados: dict):
    """Atualiza projecao local do produto no ItemEstoque."""
    from src.handlers.estoque import _get_item_by_produto, _put_item

    produto_id = dados.get("produto_id")
    if not produto_id:
        logger.error("ProdutoAtualizado sem produto_id")
        return

    item = _get_item_by_produto(produto_id)
    if not item:
        logger.warning(f"ItemEstoque nao encontrado para produto {produto_id}")
        return

    item["sku"] = dados.get("sku", item.get("sku", ""))
    item["nome_produto"] = dados.get("nome", item.get("nome_produto", ""))
    item["categoria_nome"] = dados.get("categoria_nome", item.get("categoria_nome", ""))
    item["atualizado_em"] = datetime.now(timezone.utc).isoformat()
    _put_item(item)
    logger.info(f"ItemEstoque atualizado: {item['id']} para produto {produto_id}")
