import json
import logging
from uuid import UUID, uuid4
from datetime import datetime, timezone

from src.container import container
from src.domain.entities.item_estoque import ItemEstoque

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        message = json.loads(body.get("Message", "{}"))
        evento = message.get("evento", "")
        dados = message.get("dados", {})

        if evento == "ProdutoCriado":
            _handle_produto_criado(dados)
        elif evento == "ProdutoAtualizado":
            _handle_produto_atualizado(dados)
        else:
            logger.info(f"Evento ignorado: {evento}")

    return {"statusCode": 200}


def _handle_produto_criado(dados: dict) -> None:
    produto_id = UUID(dados["produto_id"])
    repo = container.item_repo

    existing = repo.get_by_produto_id(produto_id)
    if existing is not None:
        return

    now = datetime.now(timezone.utc)
    item = ItemEstoque(
        id=uuid4(),
        produto_id=produto_id,
        sku=dados["sku"],
        nome_produto=dados["nome"],
        categoria_nome=dados["categoria_nome"],
        saldo=0,
        criado_em=now,
        atualizado_em=now,
    )
    repo.save(item)


def _handle_produto_atualizado(dados: dict) -> None:
    produto_id = UUID(dados["produto_id"])
    repo = container.item_repo

    item = repo.get_by_produto_id(produto_id)
    if item is None:
        return

    item.sku = dados.get("sku", item.sku)
    item.nome_produto = dados.get("nome", item.nome_produto)
    item.categoria_nome = dados.get("categoria_nome", item.categoria_nome)
    item.atualizado_em = datetime.now(timezone.utc)
    repo.save(item)
