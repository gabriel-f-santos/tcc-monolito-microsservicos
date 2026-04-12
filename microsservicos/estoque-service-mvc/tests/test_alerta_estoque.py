"""Testes da feature Alerta de Estoque Baixo — Microsservico Estoque DDD.
Spec: docs/features/spec-alerta-estoque-baixo.md
Invoca Lambda handlers diretamente. Usa moto via conftest.py."""
import json
import uuid

from src.handlers.estoque import handler
from src.handlers.event_consumer import handler as consumer_handler


def _event(method: str, path: str, body: dict = None) -> dict:
    return {
        "httpMethod": method,
        "path": path,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body) if body else None,
        "queryStringParameters": None,
        "requestContext": {"authorizer": {"principalId": "test-user"}},
    }


def _sqs_event(evento: str, dados: dict) -> dict:
    message = json.dumps({"evento": evento, "dados": dados})
    return {"Records": [{"body": json.dumps({"Message": message})}]}


def _criar_item() -> tuple[str, str]:
    """Cria ItemEstoque via ProdutoCriado e retorna (item_id, produto_id)."""
    pid = str(uuid.uuid4())
    consumer_handler(_sqs_event("ProdutoCriado", {
        "produto_id": pid, "sku": f"AL-{uuid.uuid4().hex[:6]}",
        "nome": "ProdAlerta", "categoria_nome": "CatTeste",
    }), None)
    resp = handler(_event("GET", f"/api/v1/estoque/produto/{pid}"), None)
    item = json.loads(resp["body"])
    return item["id"], pid


def test_configurar_alerta():
    """PATCH configurar-alerta com estoque_minimo=10 → 200."""
    item_id, _ = _criar_item()
    resp = handler(_event("PATCH", f"/api/v1/estoque/{item_id}/configurar-alerta",
                          {"estoque_minimo": 10}), None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["estoque_minimo"] == 10


def test_alerta_criado_quando_saldo_abaixo_minimo():
    """Config min=10, entrada 15, saida 10 → saldo=5, 1 alerta."""
    item_id, _ = _criar_item()
    handler(_event("PATCH", f"/api/v1/estoque/{item_id}/configurar-alerta", {"estoque_minimo": 10}), None)
    handler(_event("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 15}), None)
    handler(_event("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 10}), None)

    resp = handler(_event("GET", f"/api/v1/estoque/{item_id}/alertas"), None)
    assert resp["statusCode"] == 200
    alertas = json.loads(resp["body"])
    assert len(alertas) == 1
    assert alertas[0]["tipo"] == "ESTOQUE_BAIXO"
    assert alertas[0]["saldo_atual"] == 5
    assert alertas[0]["estoque_minimo"] == 10


def test_sem_alerta_quando_saldo_acima_minimo():
    """Config min=5, entrada 20, saida 10 → saldo=10, 0 alertas."""
    item_id, _ = _criar_item()
    handler(_event("PATCH", f"/api/v1/estoque/{item_id}/configurar-alerta", {"estoque_minimo": 5}), None)
    handler(_event("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 20}), None)
    handler(_event("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 10}), None)

    resp = handler(_event("GET", f"/api/v1/estoque/{item_id}/alertas"), None)
    assert resp["statusCode"] == 200
    assert len(json.loads(resp["body"])) == 0


def test_listar_alertas_multiplos():
    """Config min=10, entrada 20, saida 8, saida 8 → 1 alerta (saldo=4)."""
    item_id, _ = _criar_item()
    handler(_event("PATCH", f"/api/v1/estoque/{item_id}/configurar-alerta", {"estoque_minimo": 10}), None)
    handler(_event("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 20}), None)
    handler(_event("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 8}), None)  # saldo=12, ok
    handler(_event("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 8}), None)  # saldo=4, alerta

    resp = handler(_event("GET", f"/api/v1/estoque/{item_id}/alertas"), None)
    alertas = json.loads(resp["body"])
    assert len(alertas) == 1
    assert alertas[0]["saldo_atual"] == 4
