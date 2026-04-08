import json
import re
from uuid import UUID

from src.application.use_cases.registrar_entrada import RegistrarEntradaDTO
from src.application.use_cases.registrar_saida import RegistrarSaidaDTO
from src.container import EstoqueContainer
from src.infrastructure.config.settings import settings
from src.shared.domain.exceptions.base import DomainException

container = EstoqueContainer(
    itens_estoque_table=settings.itens_estoque_table,
    movimentacoes_table=settings.movimentacoes_table,
)

HEADERS = {"Content-Type": "application/json"}

STATUS_MAP = {
    "ESTOQUE_ITEM_NAO_ENCONTRADO": 404,
    "ESTOQUE_QUANTIDADE_INVALIDA": 400,
    "ESTOQUE_INSUFICIENTE": 400,
    "ESTOQUE_ITEM_INATIVO": 400,
}

UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


def _item_to_dict(item) -> dict:
    return {
        "id": str(item.id),
        "produto_id": str(item.produto_id),
        "sku": item.sku,
        "nome_produto": item.nome_produto,
        "categoria_nome": item.categoria_nome,
        "saldo": item.saldo,
        "ativo": item.ativo,
        "criado_em": item.criado_em.isoformat(),
        "atualizado_em": item.atualizado_em.isoformat(),
    }


def _movimentacao_to_dict(mov) -> dict:
    return {
        "id": str(mov.id),
        "item_estoque_id": str(mov.item_estoque_id),
        "tipo": mov.tipo.value,
        "quantidade": mov.quantidade,
        "lote": mov.lote,
        "motivo": mov.motivo,
        "criado_em": mov.criado_em.isoformat(),
        "atualizado_em": mov.atualizado_em.isoformat(),
    }


def _response(status_code: int, body: dict | list) -> dict:
    return {
        "statusCode": status_code,
        "headers": HEADERS,
        "body": json.dumps(body),
    }


def _extract_id(path: str, prefix: str) -> str | None:
    remainder = path[len(prefix):]
    if remainder.startswith("/"):
        remainder = remainder[1:]
    if remainder and UUID_PATTERN.match(remainder):
        return remainder
    return None


def handler(event, context):
    try:
        method = event["httpMethod"]
        path = event.get("path", "")

        # POST /api/v1/estoque/{id}/entrada
        if path.startswith("/api/v1/estoque/") and path.endswith("/entrada") and method == "POST":
            item_id = path.replace("/api/v1/estoque/", "").replace("/entrada", "")
            if UUID_PATTERN.match(item_id):
                body = json.loads(event["body"])
                use_case = container.registrar_entrada()
                mov = use_case.execute(RegistrarEntradaDTO(
                    item_estoque_id=UUID(item_id),
                    quantidade=body["quantidade"],
                    lote=body.get("lote"),
                    motivo=body.get("motivo"),
                ))
                return _response(201, _movimentacao_to_dict(mov))

        # POST /api/v1/estoque/{id}/saida
        if path.startswith("/api/v1/estoque/") and path.endswith("/saida") and method == "POST":
            item_id = path.replace("/api/v1/estoque/", "").replace("/saida", "")
            if UUID_PATTERN.match(item_id):
                body = json.loads(event["body"])
                use_case = container.registrar_saida()
                mov = use_case.execute(RegistrarSaidaDTO(
                    item_estoque_id=UUID(item_id),
                    quantidade=body["quantidade"],
                    motivo=body.get("motivo"),
                ))
                return _response(201, _movimentacao_to_dict(mov))

        # GET /api/v1/estoque/{id}/movimentacoes
        if path.startswith("/api/v1/estoque/") and path.endswith("/movimentacoes") and method == "GET":
            item_id = path.replace("/api/v1/estoque/", "").replace("/movimentacoes", "")
            if UUID_PATTERN.match(item_id):
                params = event.get("queryStringParameters") or {}
                use_case = container.listar_movimentacoes()
                movs = use_case.execute(
                    item_estoque_id=UUID(item_id),
                    tipo=params.get("tipo"),
                    page=int(params.get("page", 1)),
                    size=int(params.get("size", 20)),
                )
                return _response(200, [_movimentacao_to_dict(m) for m in movs])

        # GET /api/v1/estoque/produto/{produto_id}
        if path.startswith("/api/v1/estoque/produto/") and method == "GET":
            produto_id = _extract_id(path, "/api/v1/estoque/produto")
            if produto_id:
                use_case = container.buscar_item()
                item = use_case.execute_por_produto(UUID(produto_id))
                return _response(200, _item_to_dict(item))

        # GET /api/v1/estoque/{id}
        if path.startswith("/api/v1/estoque/") and method == "GET":
            item_id = _extract_id(path, "/api/v1/estoque")
            if item_id:
                use_case = container.buscar_item()
                item = use_case.execute(UUID(item_id))
                return _response(200, _item_to_dict(item))

        # GET /api/v1/estoque
        if path == "/api/v1/estoque" and method == "GET":
            params = event.get("queryStringParameters") or {}
            saldo_min = int(params["saldo_min"]) if "saldo_min" in params else None
            use_case = container.listar_itens()
            itens = use_case.execute(
                saldo_min=saldo_min,
                page=int(params.get("page", 1)),
                size=int(params.get("size", 20)),
            )
            return _response(200, [_item_to_dict(i) for i in itens])

        return _response(404, {"code": "ROTA_NAO_ENCONTRADA", "detail": "Rota nao encontrada"})

    except DomainException as exc:
        return _response(STATUS_MAP.get(exc.code, 400), {"code": exc.code, "detail": exc.message})
