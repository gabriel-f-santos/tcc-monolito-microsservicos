"""Lambda handler para o Catalogo Service.

Roteamento por httpMethod + path. Composition root construido por request
(stateless) — repositorios DynamoDB e publisher SNS lazy-cached dentro dos
objetos. Env vars lidas dentro do handler para respeitar o contrato
(sem chamadas AWS em import time)."""
from __future__ import annotations

import json
import os
import re
from decimal import Decimal, InvalidOperation
from uuid import UUID

from src.application.dtos import (
    AtualizarProdutoDTO,
    CriarCategoriaDTO,
    CriarProdutoDTO,
)
from src.application.use_cases import (
    AtualizarProdutoUseCase,
    BuscarCategoriaUseCase,
    BuscarProdutoUseCase,
    CriarCategoriaUseCase,
    CriarProdutoUseCase,
    DesativarProdutoUseCase,
    ListarCategoriasUseCase,
    ListarProdutosUseCase,
)
from src.domain.entities import Categoria, Produto
from src.domain.exceptions import (
    CategoriaNaoEncontrada,
    CategoriaNomeDuplicado,
    ProdutoNaoEncontrado,
    ProdutoSkuDuplicado,
)
from src.infrastructure.dynamodb_categoria_repository import (
    DynamoDBCategoriaRepository,
)
from src.infrastructure.dynamodb_produto_repository import DynamoDBProdutoRepository
from src.infrastructure.sns_event_publisher import SnsEventPublisher
from src.shared.exceptions import DomainException


# --- Serializers --------------------------------------------------------------


def _categoria_to_dict(c: Categoria) -> dict:
    return {
        "id": str(c.id),
        "nome": c.nome,
        "descricao": c.descricao,
        "criado_em": c.criado_em.isoformat(),
        "atualizado_em": c.atualizado_em.isoformat(),
    }


def _produto_to_dict(p: Produto) -> dict:
    return {
        "id": str(p.id),
        "sku": p.sku.valor,
        "nome": p.nome,
        "descricao": p.descricao,
        "preco": str(p.preco.valor),
        "categoria_id": str(p.categoria_id),
        "ativo": p.ativo,
        "criado_em": p.criado_em.isoformat(),
        "atualizado_em": p.atualizado_em.isoformat(),
    }


def _response(status: int, body) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body) if body is not None else "",
    }


def _error(status: int, code: str, message: str) -> dict:
    return _response(status, {"error": code, "message": message})


# --- Composition root (per-invocation) ---------------------------------------


def _build_container():
    categoria_repo = DynamoDBCategoriaRepository(os.environ["CATEGORIAS_TABLE"])
    produto_repo = DynamoDBProdutoRepository(os.environ["PRODUTOS_TABLE"])
    publisher = SnsEventPublisher(os.environ["EVENTOS_TOPIC_ARN"])
    return {
        "criar_categoria": CriarCategoriaUseCase(categoria_repo),
        "listar_categorias": ListarCategoriasUseCase(categoria_repo),
        "buscar_categoria": BuscarCategoriaUseCase(categoria_repo),
        "criar_produto": CriarProdutoUseCase(produto_repo, categoria_repo, publisher),
        "listar_produtos": ListarProdutosUseCase(produto_repo),
        "buscar_produto": BuscarProdutoUseCase(produto_repo),
        "atualizar_produto": AtualizarProdutoUseCase(produto_repo),
        "desativar_produto": DesativarProdutoUseCase(produto_repo),
    }


# --- Routing ------------------------------------------------------------------

_CATEGORIA_BY_ID = re.compile(r"^/api/v1/categorias/(?P<id>[^/]+)$")
_PRODUTO_BY_ID = re.compile(r"^/api/v1/produtos/(?P<id>[^/]+)$")
_PRODUTO_DESATIVAR = re.compile(r"^/api/v1/produtos/(?P<id>[^/]+)/desativar$")


def _parse_body(event: dict) -> dict:
    raw = event.get("body")
    if not raw:
        return {}
    if isinstance(raw, (dict, list)):
        return raw
    return json.loads(raw)


def _parse_uuid(raw: str) -> UUID:
    return UUID(raw)


def handler(event, context):  # noqa: C901 — dispatch table
    method = event.get("httpMethod", "").upper()
    path = event.get("path", "")
    query = event.get("queryStringParameters") or {}

    try:
        container = _build_container()

        # --- Categorias ---
        if path == "/api/v1/categorias":
            if method == "POST":
                body = _parse_body(event)
                dto = CriarCategoriaDTO(
                    nome=body.get("nome", ""),
                    descricao=body.get("descricao"),
                )
                categoria = container["criar_categoria"].execute(dto)
                return _response(201, _categoria_to_dict(categoria))
            if method == "GET":
                categorias = container["listar_categorias"].execute()
                return _response(200, [_categoria_to_dict(c) for c in categorias])
            return _error(405, "METODO_NAO_PERMITIDO", f"Metodo {method} nao permitido")

        m = _CATEGORIA_BY_ID.match(path)
        if m:
            cid = _parse_uuid(m.group("id"))
            if method == "GET":
                categoria = container["buscar_categoria"].execute(cid)
                return _response(200, _categoria_to_dict(categoria))
            return _error(405, "METODO_NAO_PERMITIDO", f"Metodo {method} nao permitido")

        # --- Produtos ---
        m = _PRODUTO_DESATIVAR.match(path)
        if m:
            pid = _parse_uuid(m.group("id"))
            if method == "PATCH":
                produto = container["desativar_produto"].execute(pid)
                return _response(200, _produto_to_dict(produto))
            return _error(405, "METODO_NAO_PERMITIDO", f"Metodo {method} nao permitido")

        m = _PRODUTO_BY_ID.match(path)
        if m:
            pid = _parse_uuid(m.group("id"))
            if method == "GET":
                produto = container["buscar_produto"].execute(pid)
                return _response(200, _produto_to_dict(produto))
            if method == "PUT":
                body = _parse_body(event)
                preco_raw = body.get("preco")
                dto = AtualizarProdutoDTO(
                    nome=body.get("nome"),
                    descricao=body.get("descricao"),
                    preco=Decimal(str(preco_raw)) if preco_raw is not None else None,
                )
                produto = container["atualizar_produto"].execute(pid, dto)
                return _response(200, _produto_to_dict(produto))
            return _error(405, "METODO_NAO_PERMITIDO", f"Metodo {method} nao permitido")

        if path == "/api/v1/produtos":
            if method == "POST":
                body = _parse_body(event)
                try:
                    preco = Decimal(str(body.get("preco", "0")))
                except (InvalidOperation, ValueError):
                    return _error(422, "PRECO_INVALIDO", "Preco invalido")
                try:
                    categoria_id = _parse_uuid(body.get("categoria_id", ""))
                except (ValueError, TypeError):
                    return _error(404, "CATEGORIA_NAO_ENCONTRADA", "Categoria nao encontrada")
                dto = CriarProdutoDTO(
                    sku=body.get("sku", ""),
                    nome=body.get("nome", ""),
                    preco=preco,
                    categoria_id=categoria_id,
                    descricao=body.get("descricao"),
                )
                produto = container["criar_produto"].execute(dto)
                return _response(201, _produto_to_dict(produto))
            if method == "GET":
                cat_id_raw = query.get("categoria_id") if query else None
                ativo_raw = query.get("ativo") if query else None
                categoria_id = _parse_uuid(cat_id_raw) if cat_id_raw else None
                ativo = None
                if ativo_raw is not None:
                    ativo = str(ativo_raw).lower() in ("true", "1", "yes")
                produtos = container["listar_produtos"].execute(
                    categoria_id=categoria_id, ativo=ativo
                )
                return _response(200, [_produto_to_dict(p) for p in produtos])
            return _error(405, "METODO_NAO_PERMITIDO", f"Metodo {method} nao permitido")

        return _error(404, "ROTA_NAO_ENCONTRADA", f"Rota {method} {path} nao encontrada")

    except CategoriaNomeDuplicado as e:
        return _error(409, e.code, e.message)
    except ProdutoSkuDuplicado as e:
        return _error(409, e.code, e.message)
    except CategoriaNaoEncontrada as e:
        return _error(404, e.code, e.message)
    except ProdutoNaoEncontrado as e:
        return _error(404, e.code, e.message)
    except DomainException as e:
        # Erros de invariante de dominio (SKU invalido, preco <= 0, nome vazio)
        return _error(422, e.code, e.message)
