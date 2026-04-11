"""Event consumer: SQS → SNS envelope → ProdutoCriado/Atualizado/Desativado.

Persiste a projecao local de ItemEstoque no DynamoDB a cada evento do catalogo.
Idempotente: se ja existe item para o produto_id, ProdutoCriado e ignorado.
"""
from __future__ import annotations

import json
import logging
import os
from uuid import UUID

from src.domain.entities.item_estoque import ItemEstoque
from src.infrastructure.repositories.dynamodb_item_estoque_repository import (
    DynamoDBItemEstoqueRepository,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _repo() -> DynamoDBItemEstoqueRepository:
    return DynamoDBItemEstoqueRepository(os.environ["ITENS_ESTOQUE_TABLE"])


def _handle_produto_criado(repo: DynamoDBItemEstoqueRepository, dados: dict) -> None:
    produto_id = UUID(dados["produto_id"])
    # Idempotencia: ProdutoCriado 2x nao duplica
    existente = repo.get_by_produto_id(produto_id)
    if existente is not None:
        logger.info(f"ProdutoCriado ignorado (ja existe): {produto_id}")
        return

    item = ItemEstoque(
        produto_id=produto_id,
        sku=dados["sku"],
        nome_produto=dados.get("nome") or dados.get("nome_produto"),
        categoria_nome=dados.get("categoria_nome") or dados.get("categoria"),
        saldo=0,
        ativo=True,
    )
    repo.save(item)
    logger.info(f"ProdutoCriado persistido: produto_id={produto_id} item_id={item.id}")


def _handle_produto_atualizado(repo: DynamoDBItemEstoqueRepository, dados: dict) -> None:
    produto_id = UUID(dados["produto_id"])
    existente = repo.get_by_produto_id(produto_id)
    if existente is None:
        # Ainda nao chegou o ProdutoCriado — cria projecao agora.
        item = ItemEstoque(
            produto_id=produto_id,
            sku=dados.get("sku", "DESCONHECIDO"),
            nome_produto=dados.get("nome") or dados.get("nome_produto") or "",
            categoria_nome=dados.get("categoria_nome") or dados.get("categoria") or "",
            saldo=0,
            ativo=True,
        )
        repo.save(item)
        return

    if "sku" in dados and dados["sku"] is not None:
        existente.sku = dados["sku"]
    novo_nome = dados.get("nome") or dados.get("nome_produto")
    if novo_nome is not None:
        existente.nome_produto = novo_nome
    nova_cat = dados.get("categoria_nome") or dados.get("categoria")
    if nova_cat is not None:
        existente.categoria_nome = nova_cat
    repo.save(existente)


def _handle_produto_desativado(repo: DynamoDBItemEstoqueRepository, dados: dict) -> None:
    produto_id = UUID(dados["produto_id"])
    existente = repo.get_by_produto_id(produto_id)
    if existente is None:
        return
    existente.ativo = False
    repo.save(existente)


def handler(event, context):
    repo = _repo()
    # Itera mesmo com BatchSize=1 — Lambda pode entregar multiplos em retry.
    for record in event.get("Records", []):
        sqs_body = json.loads(record["body"])  # camada 1: envelope SNS
        # Suporta envelope SNS completo e payload direto (para testes).
        if "Message" in sqs_body:
            message = json.loads(sqs_body["Message"])  # camada 2: payload real
        else:
            message = sqs_body
        evento = message.get("evento")
        dados = message.get("dados") or {}

        if evento == "ProdutoCriado":
            _handle_produto_criado(repo, dados)
        elif evento == "ProdutoAtualizado":
            _handle_produto_atualizado(repo, dados)
        elif evento == "ProdutoDesativado":
            _handle_produto_desativado(repo, dados)
        else:
            logger.warning(f"Evento desconhecido: {evento}")

    return {"statusCode": 200}
