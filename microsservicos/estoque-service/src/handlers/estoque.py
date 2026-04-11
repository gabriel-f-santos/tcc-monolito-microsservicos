import json
import re
from uuid import UUID

from src.container import container
from src.application.use_cases.registrar_entrada import RegistrarEntradaDTO
from src.application.use_cases.registrar_saida import RegistrarSaidaDTO
from src.shared.domain.exceptions.base import DomainException
from src.domain.exceptions.estoque import ItemNaoEncontrado, QuantidadeInvalida, EstoqueInsuficiente

HEADERS = {"Content-Type": "application/json"}

# Route patterns
RE_ITEM_ENTRADA = re.compile(r"^/api/v1/estoque/([^/]+)/entrada$")
RE_ITEM_SAIDA = re.compile(r"^/api/v1/estoque/([^/]+)/saida$")
RE_ITEM_MOVS = re.compile(r"^/api/v1/estoque/([^/]+)/movimentacoes$")
RE_ITEM_POR_PRODUTO = re.compile(r"^/api/v1/estoque/produto/([^/]+)$")
RE_ITEM_BY_ID = re.compile(r"^/api/v1/estoque/([^/]+)$")
RE_LIST = re.compile(r"^/api/v1/estoque/?$")


def _json_response(status: int, body) -> dict:
    return {"statusCode": status, "headers": HEADERS, "body": json.dumps(body)}


def _serialize_item(item) -> dict:
    return {
        "id": str(item.id),
        "produto_id": str(item.produto_id),
        "sku": item.sku,
        "nome_produto": item.nome_produto,
        "categoria_nome": item.categoria_nome,
        "saldo": item.saldo,
        "ativo": item.ativo,
    }


def _serialize_mov(mov) -> dict:
    return {
        "id": str(mov.id),
        "item_estoque_id": str(mov.item_estoque_id),
        "tipo": mov.tipo.value,
        "quantidade": mov.quantidade,
        "lote": mov.lote,
        "motivo": mov.motivo,
    }


def handler(event, context):
    method = event.get("httpMethod", "")
    path = event.get("path", "")
    body = json.loads(event["body"]) if event.get("body") else {}

    try:
        # POST /estoque/{id}/entrada
        m = RE_ITEM_ENTRADA.match(path)
        if m and method == "POST":
            item_id = UUID(m.group(1))
            dto = RegistrarEntradaDTO(
                item_estoque_id=item_id,
                quantidade=body.get("quantidade", 0),
                lote=body.get("lote"),
                motivo=body.get("motivo"),
            )
            mov = container.registrar_entrada_use_case().execute(dto)
            return _json_response(201, _serialize_mov(mov))

        # POST /estoque/{id}/saida
        m = RE_ITEM_SAIDA.match(path)
        if m and method == "POST":
            item_id = UUID(m.group(1))
            dto = RegistrarSaidaDTO(
                item_estoque_id=item_id,
                quantidade=body.get("quantidade", 0),
                motivo=body.get("motivo"),
            )
            mov = container.registrar_saida_use_case().execute(dto)
            return _json_response(201, _serialize_mov(mov))

        # GET /estoque/{id}/movimentacoes
        m = RE_ITEM_MOVS.match(path)
        if m and method == "GET":
            item_id = UUID(m.group(1))
            movs = container.listar_movimentacoes_use_case().execute(item_estoque_id=item_id)
            return _json_response(200, [_serialize_mov(mv) for mv in movs])

        # GET /estoque/produto/{produto_id}
        m = RE_ITEM_POR_PRODUTO.match(path)
        if m and method == "GET":
            produto_id = UUID(m.group(1))
            item = container.buscar_item_use_case().execute_por_produto(produto_id)
            return _json_response(200, _serialize_item(item))

        # GET /estoque/{id}
        m = RE_ITEM_BY_ID.match(path)
        if m and method == "GET":
            item_id = UUID(m.group(1))
            item = container.buscar_item_use_case().execute(item_id)
            return _json_response(200, _serialize_item(item))

        # GET /estoque
        m = RE_LIST.match(path)
        if m and method == "GET":
            items = container.listar_itens_use_case().execute()
            return _json_response(200, [_serialize_item(i) for i in items])

        return _json_response(404, {"message": "Not found"})

    except ItemNaoEncontrado:
        return _json_response(404, {"message": "Item nao encontrado"})
    except (QuantidadeInvalida, EstoqueInsuficiente) as e:
        return _json_response(422, {"message": e.message, "code": e.code})
    except DomainException as e:
        return _json_response(422, {"message": e.message, "code": e.code})
