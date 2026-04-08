import json
import re
from decimal import Decimal
from uuid import UUID

from src.application.use_cases.atualizar_produto import AtualizarProdutoDTO
from src.application.use_cases.criar_categoria import CriarCategoriaDTO
from src.application.use_cases.criar_produto import CriarProdutoDTO
from src.container import CatalogoContainer
from src.infrastructure.config.settings import settings
from src.shared.domain.exceptions.base import DomainException

container = CatalogoContainer(
    produtos_table=settings.produtos_table,
    categorias_table=settings.categorias_table,
    eventos_topic_arn=settings.eventos_topic_arn,
)

HEADERS = {"Content-Type": "application/json"}

STATUS_MAP = {
    "CATEGORIA_NOME_DUPLICADO": 409,
    "CATEGORIA_NAO_ENCONTRADA": 404,
    "PRODUTO_SKU_DUPLICADO": 409,
    "PRODUTO_NAO_ENCONTRADO": 404,
}

UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


def _produto_to_dict(produto) -> dict:
    return {
        "id": str(produto.id),
        "sku": produto.sku.valor,
        "nome": produto.nome,
        "descricao": produto.descricao,
        "preco": str(produto.preco.valor),
        "categoria_id": str(produto.categoria_id),
        "ativo": produto.ativo,
        "criado_em": produto.criado_em.isoformat(),
        "atualizado_em": produto.atualizado_em.isoformat(),
    }


def _categoria_to_dict(categoria) -> dict:
    return {
        "id": str(categoria.id),
        "nome": categoria.nome,
        "descricao": categoria.descricao,
        "criado_em": categoria.criado_em.isoformat(),
        "atualizado_em": categoria.atualizado_em.isoformat(),
    }


def _response(status_code: int, body: dict | list) -> dict:
    return {
        "statusCode": status_code,
        "headers": HEADERS,
        "body": json.dumps(body),
    }


def _extract_id(path: str, prefix: str) -> str | None:
    """Extract UUID from path like /api/v1/produtos/{id}"""
    remainder = path[len(prefix):]
    if remainder.startswith("/"):
        remainder = remainder[1:]
    if remainder and UUID_PATTERN.match(remainder):
        return remainder
    return None


def handler(event, context):
    """Handler para CRUD de produtos e categorias.
    Roteamento por httpMethod + path.
    """
    try:
        method = event["httpMethod"]
        path = event.get("path", "")
        user_id = event.get("requestContext", {}).get("authorizer", {}).get("principalId")

        # --- Categorias ---
        if path == "/api/v1/categorias" and method == "POST":
            body = json.loads(event["body"])
            use_case = container.criar_categoria()
            categoria = use_case.execute(CriarCategoriaDTO(**body))
            return _response(201, _categoria_to_dict(categoria))

        if path == "/api/v1/categorias" and method == "GET":
            use_case = container.listar_categorias()
            categorias = use_case.execute()
            return _response(200, [_categoria_to_dict(c) for c in categorias])

        if path.startswith("/api/v1/categorias/") and method == "GET":
            cat_id = _extract_id(path, "/api/v1/categorias")
            if cat_id:
                use_case = container.buscar_categoria()
                categoria = use_case.execute(UUID(cat_id))
                return _response(200, _categoria_to_dict(categoria))

        # --- Produtos ---
        if path == "/api/v1/produtos" and method == "POST":
            body = json.loads(event["body"])
            body["categoria_id"] = UUID(body["categoria_id"])
            body["preco"] = Decimal(str(body["preco"]))
            use_case = container.criar_produto()
            produto = use_case.execute(CriarProdutoDTO(**body))
            return _response(201, _produto_to_dict(produto))

        if path == "/api/v1/produtos" and method == "GET":
            params = event.get("queryStringParameters") or {}
            cat_id = UUID(params["categoria_id"]) if "categoria_id" in params else None
            use_case = container.listar_produtos()
            produtos = use_case.execute(categoria_id=cat_id)
            return _response(200, [_produto_to_dict(p) for p in produtos])

        if path.startswith("/api/v1/produtos/") and method == "GET":
            prod_id = _extract_id(path, "/api/v1/produtos")
            if prod_id:
                use_case = container.buscar_produto()
                produto = use_case.execute(UUID(prod_id))
                return _response(200, _produto_to_dict(produto))

        if path.startswith("/api/v1/produtos/") and method == "PUT":
            prod_id = _extract_id(path, "/api/v1/produtos")
            if prod_id:
                body = json.loads(event["body"])
                if "preco" in body:
                    body["preco"] = Decimal(str(body["preco"]))
                use_case = container.atualizar_produto()
                produto = use_case.execute(UUID(prod_id), AtualizarProdutoDTO(**body))
                return _response(200, _produto_to_dict(produto))

        if path.startswith("/api/v1/produtos/") and method == "PATCH" and path.endswith("/desativar"):
            prod_id = _extract_id(path, "/api/v1/produtos")
            if prod_id:
                use_case = container.desativar_produto()
                produto = use_case.execute(UUID(prod_id))
                return _response(200, _produto_to_dict(produto))

        return _response(404, {"code": "ROTA_NAO_ENCONTRADA", "detail": "Rota nao encontrada"})

    except DomainException as exc:
        return _response(STATUS_MAP.get(exc.code, 400), {"code": exc.code, "detail": exc.message})
