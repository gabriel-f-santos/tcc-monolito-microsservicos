import json
import re
from decimal import Decimal
from uuid import UUID

from src.container import container
from src.application.use_cases.criar_categoria import CriarCategoriaDTO
from src.application.use_cases.criar_produto import CriarProdutoDTO
from src.application.use_cases.atualizar_produto import AtualizarProdutoDTO
from src.domain.exceptions.catalogo import (
    CategoriaNaoEncontrada,
    CategoriaNomeDuplicado,
    ProdutoNaoEncontrado,
    ProdutoSkuDuplicado,
)
from src.shared.domain.exceptions.base import DomainException

HEADERS = {"Content-Type": "application/json"}

# Route patterns
RE_CATEGORIAS = re.compile(r"^/api/v1/categorias$")
RE_CATEGORIA_ID = re.compile(r"^/api/v1/categorias/([^/]+)$")
RE_PRODUTOS = re.compile(r"^/api/v1/produtos$")
RE_PRODUTO_ID = re.compile(r"^/api/v1/produtos/([^/]+)$")
RE_PRODUTO_DESATIVAR = re.compile(r"^/api/v1/produtos/([^/]+)/desativar$")


def _response(status: int, body):
    return {"statusCode": status, "headers": HEADERS, "body": json.dumps(body, default=str)}


def _parse_body(event) -> dict:
    raw = event.get("body")
    if raw:
        return json.loads(raw)
    return {}


def handler(event, context):
    method = event["httpMethod"]
    path = event["path"]

    try:
        # --- Produto desativar (must match before produto by id) ---
        m = RE_PRODUTO_DESATIVAR.match(path)
        if m and method == "PATCH":
            produto_id = UUID(m.group(1))
            produto = container["desativar_produto"].execute(produto_id)
            return _response(200, _produto_to_dict(produto))

        # --- Categorias collection ---
        if RE_CATEGORIAS.match(path):
            if method == "POST":
                body = _parse_body(event)
                dto = CriarCategoriaDTO(nome=body["nome"], descricao=body.get("descricao", ""))
                cat = container["criar_categoria"].execute(dto)
                return _response(201, _categoria_to_dict(cat))
            if method == "GET":
                cats = container["listar_categorias"].execute()
                return _response(200, [_categoria_to_dict(c) for c in cats])

        # --- Categoria by id ---
        m = RE_CATEGORIA_ID.match(path)
        if m and method == "GET":
            cat_id = UUID(m.group(1))
            cat = container["buscar_categoria"].execute(cat_id)
            return _response(200, _categoria_to_dict(cat))

        # --- Produtos collection ---
        if RE_PRODUTOS.match(path):
            if method == "POST":
                body = _parse_body(event)
                dto = CriarProdutoDTO(
                    sku=body["sku"],
                    nome=body["nome"],
                    preco=Decimal(str(body["preco"])),
                    categoria_id=UUID(body["categoria_id"]),
                    descricao=body.get("descricao"),
                )
                produto = container["criar_produto"].execute(dto)
                return _response(201, _produto_to_dict(produto))
            if method == "GET":
                query = event.get("queryStringParameters") or {}
                cat_id = UUID(query["categoria_id"]) if "categoria_id" in query else None
                produtos = container["listar_produtos"].execute(categoria_id=cat_id)
                return _response(200, [_produto_to_dict(p) for p in produtos])

        # --- Produto by id ---
        m = RE_PRODUTO_ID.match(path)
        if m:
            produto_id = UUID(m.group(1))
            if method == "GET":
                produto = container["buscar_produto"].execute(produto_id)
                return _response(200, _produto_to_dict(produto))
            if method == "PUT":
                body = _parse_body(event)
                dto = AtualizarProdutoDTO(
                    nome=body.get("nome"),
                    descricao=body.get("descricao"),
                    preco=Decimal(str(body["preco"])) if "preco" in body else None,
                )
                produto = container["atualizar_produto"].execute(produto_id, dto)
                return _response(200, _produto_to_dict(produto))

        return _response(404, {"message": "Not found"})

    except CategoriaNomeDuplicado:
        return _response(409, {"message": "Nome de categoria ja existe"})
    except ProdutoSkuDuplicado:
        return _response(409, {"message": "SKU ja existe"})
    except CategoriaNaoEncontrada:
        return _response(404, {"message": "Categoria nao encontrada"})
    except ProdutoNaoEncontrado:
        return _response(404, {"message": "Produto nao encontrado"})
    except DomainException as e:
        return _response(422, {"message": e.message, "code": e.code})


def _categoria_to_dict(cat) -> dict:
    return {
        "id": str(cat.id),
        "nome": cat.nome,
        "descricao": cat.descricao,
        "criado_em": cat.criado_em.isoformat(),
        "atualizado_em": cat.atualizado_em.isoformat(),
    }


def _produto_to_dict(prod) -> dict:
    return {
        "id": str(prod.id),
        "sku": prod.sku.valor,
        "nome": prod.nome,
        "descricao": prod.descricao,
        "preco": float(prod.preco.valor),
        "categoria_id": str(prod.categoria_id),
        "ativo": prod.ativo,
        "criado_em": prod.criado_em.isoformat(),
        "atualizado_em": prod.atualizado_em.isoformat(),
    }
