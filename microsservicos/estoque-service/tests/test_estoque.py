"""Testes de comportamento do Estoque Service.
Identicos entre DDD e MVC — mesmos payloads, mesmas respostas.
Invoca Lambda handlers com event mockado.

NOTA: Estes testes assumem que o ItemEstoque ja existe (criado via evento ou setup).
O conftest.py deve prover um helper para criar itens de estoque para teste."""
import json
import uuid

from src.handlers.estoque import handler as estoque_handler
from src.handlers.event_consumer import handler as consumer_handler


def _event(method: str, path: str, body: dict = None, query: dict = None) -> dict:
    return {
        "httpMethod": method,
        "path": path,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body) if body else None,
        "queryStringParameters": query,
        "requestContext": {"authorizer": {"principalId": "test-user"}},
    }


def _sqs_event(evento: str, dados: dict) -> dict:
    """Simula um evento SQS vindo do SNS."""
    message = json.dumps({"evento": evento, "dados": dados})
    return {
        "Records": [{"body": json.dumps({"Message": message})}],
    }


def _unique():
    return str(uuid.uuid4())


def _criar_item_via_evento(produto_id: str = None, sku: str = None):
    """Cria ItemEstoque via evento ProdutoCriado (simula SNS→SQS)."""
    pid = produto_id or _unique()
    event = _sqs_event("ProdutoCriado", {
        "produto_id": pid,
        "sku": sku or f"SKU-{uuid.uuid4().hex[:6]}",
        "nome": "Produto Teste",
        "categoria_nome": "Categoria Teste",
    })
    consumer_handler(event, None)
    # Buscar o item criado
    resp = estoque_handler(_event("GET", f"/api/v1/estoque/produto/{pid}"), None)
    if resp["statusCode"] == 200:
        return json.loads(resp["body"])["id"], pid
    return None, pid


# === Entrada ===

def test_registrar_entrada():
    """POST /estoque/{id}/entrada → 201 + movimentacao ENTRADA."""
    item_id, _ = _criar_item_via_evento()
    resp = estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/entrada", {
        "quantidade": 100, "lote": "NF-001", "motivo": "Recebimento",
    }), None)
    assert resp["statusCode"] == 201
    body = json.loads(resp["body"])
    assert body["tipo"] == "ENTRADA"
    assert body["quantidade"] == 100


def test_saldo_apos_entrada():
    """Entrada 100 + 50 → saldo=150."""
    item_id, _ = _criar_item_via_evento()
    estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 100}), None)
    estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 50}), None)
    resp = estoque_handler(_event("GET", f"/api/v1/estoque/{item_id}"), None)
    assert json.loads(resp["body"])["saldo"] == 150


def test_entrada_quantidade_invalida():
    """POST com quantidade=0 → 422."""
    item_id, _ = _criar_item_via_evento()
    resp = estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 0}), None)
    assert resp["statusCode"] == 422


def test_entrada_item_inexistente():
    """POST /estoque/{uuid}/entrada → 404."""
    resp = estoque_handler(_event("POST", f"/api/v1/estoque/{_unique()}/entrada", {"quantidade": 10}), None)
    assert resp["statusCode"] == 404


# === Consultas ===

def test_listar_itens_estoque():
    """Criar 2 itens → GET /estoque → lista."""
    _criar_item_via_evento()
    _criar_item_via_evento()
    resp = estoque_handler(_event("GET", "/api/v1/estoque"), None)
    assert resp["statusCode"] == 200
    assert len(json.loads(resp["body"])) >= 2


def test_buscar_item_por_produto():
    """GET /estoque/produto/{produto_id} → 200."""
    _, produto_id = _criar_item_via_evento()
    resp = estoque_handler(_event("GET", f"/api/v1/estoque/produto/{produto_id}"), None)
    assert resp["statusCode"] == 200
    assert json.loads(resp["body"])["produto_id"] == produto_id


def test_historico_movimentacoes():
    """3 entradas → GET movimentacoes → 3."""
    item_id, _ = _criar_item_via_evento()
    for _ in range(3):
        estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 10}), None)
    resp = estoque_handler(_event("GET", f"/api/v1/estoque/{item_id}/movimentacoes"), None)
    assert resp["statusCode"] == 200
    assert len(json.loads(resp["body"])) == 3


# === Saida ===

def test_registrar_saida():
    """Entrada 100 + Saida 30 → saldo=70."""
    item_id, _ = _criar_item_via_evento()
    estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 100}), None)
    resp = estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 30, "motivo": "Venda"}), None)
    assert resp["statusCode"] == 201
    item = json.loads(estoque_handler(_event("GET", f"/api/v1/estoque/{item_id}"), None)["body"])
    assert item["saldo"] == 70


def test_saida_estoque_insuficiente():
    """Entrada 10 + Saida 20 → 422."""
    item_id, _ = _criar_item_via_evento()
    estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 10}), None)
    resp = estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 20}), None)
    assert resp["statusCode"] == 422


def test_saida_zera_estoque():
    """Entrada 50 + Saida 50 → saldo=0."""
    item_id, _ = _criar_item_via_evento()
    estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 50}), None)
    estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 50}), None)
    item = json.loads(estoque_handler(_event("GET", f"/api/v1/estoque/{item_id}"), None)["body"])
    assert item["saldo"] == 0


def test_multiplas_movimentacoes():
    """Entrada 100, saida 30, saida 30 → saldo=40, 3 movimentacoes."""
    item_id, _ = _criar_item_via_evento()
    estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 100}), None)
    estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 30}), None)
    estoque_handler(_event("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 30}), None)
    item = json.loads(estoque_handler(_event("GET", f"/api/v1/estoque/{item_id}"), None)["body"])
    assert item["saldo"] == 40
    movs = json.loads(estoque_handler(_event("GET", f"/api/v1/estoque/{item_id}/movimentacoes"), None)["body"])
    assert len(movs) == 3


# === Eventos ===

def test_evento_produto_criado_cria_item():
    """ProdutoCriado → ItemEstoque criado com saldo=0."""
    item_id, _ = _criar_item_via_evento()
    assert item_id is not None
    resp = estoque_handler(_event("GET", f"/api/v1/estoque/{item_id}"), None)
    assert json.loads(resp["body"])["saldo"] == 0


def test_evento_idempotente():
    """Mesmo evento 2x → 1 item só."""
    produto_id = _unique()
    dados = {"produto_id": produto_id, "sku": "IDEMP-001", "nome": "Idemp", "categoria_nome": "Cat"}
    consumer_handler(_sqs_event("ProdutoCriado", dados), None)
    consumer_handler(_sqs_event("ProdutoCriado", dados), None)
    resp = estoque_handler(_event("GET", f"/api/v1/estoque/produto/{produto_id}"), None)
    assert resp["statusCode"] == 200


def test_evento_produto_atualizado():
    """ProdutoAtualizado → projecao local atualizada."""
    produto_id = _unique()
    consumer_handler(_sqs_event("ProdutoCriado", {
        "produto_id": produto_id, "sku": "UPD-001", "nome": "Original", "categoria_nome": "CatA",
    }), None)
    consumer_handler(_sqs_event("ProdutoAtualizado", {
        "produto_id": produto_id, "sku": "UPD-001", "nome": "Atualizado", "categoria_nome": "CatB",
    }), None)
    resp = estoque_handler(_event("GET", f"/api/v1/estoque/produto/{produto_id}"), None)
    body = json.loads(resp["body"])
    assert body["nome_produto"] == "Atualizado"
    assert body["categoria_nome"] == "CatB"
