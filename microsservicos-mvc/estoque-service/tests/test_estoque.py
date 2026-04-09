"""Estoque tests — 14 testes (11 estoque + 3 eventos) com fake DynamoDB in-memory."""
import json
import uuid

import pytest

from src.handlers import estoque, event_consumer


# ---------------------------------------------------------------------------
# Fake DynamoDB table (in-memory dict)
# ---------------------------------------------------------------------------
class FakeTable:
    def __init__(self):
        self._items = {}

    def put_item(self, Item):
        self._items[Item["id"]] = dict(Item)

    def get_item(self, Key):
        item = self._items.get(Key["id"])
        if item:
            return {"Item": dict(item)}
        return {}

    def scan(self, FilterExpression=None):
        items = list(self._items.values())
        if FilterExpression is not None:
            items = [i for i in items if self._match(i, FilterExpression)]
        return {"Items": items}

    def update_item(self, Key, UpdateExpression, ExpressionAttributeValues):
        item = self._items.get(Key["id"])
        if not item:
            return
        # Parse simple "SET k1 = :v1, k2 = :v2" expressions
        set_part = UpdateExpression.replace("SET ", "")
        assignments = [a.strip() for a in set_part.split(",")]
        for assignment in assignments:
            field, placeholder = [x.strip() for x in assignment.split("=")]
            item[field] = ExpressionAttributeValues[placeholder]

    @staticmethod
    def _match(item, expr):
        # boto3 Equals: expr._values = (Attr("field"), value)
        # Attr has .name attribute
        field = expr._values[0].name
        value = expr._values[1]
        return item.get(field) == value


@pytest.fixture(autouse=True)
def _patch_tables(monkeypatch):
    """Replace DynamoDB tables with in-memory fakes for every test."""
    itens_table = FakeTable()
    movs_table = FakeTable()

    monkeypatch.setattr(estoque, "_itens_table", itens_table)
    monkeypatch.setattr(estoque, "_movs_table", movs_table)
    monkeypatch.setattr(event_consumer, "_table", itens_table)

    # Also patch _get_*_table to return fakes (prevents boto3 calls)
    monkeypatch.setattr(estoque, "_get_itens_table", lambda: itens_table)
    monkeypatch.setattr(estoque, "_get_movs_table", lambda: movs_table)
    monkeypatch.setattr(event_consumer, "_get_table", lambda: itens_table)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _create_item(produto_id=None, sku="SKU-001", nome="Produto Teste", ativo=True):
    """Create an item de estoque directly in the fake table via event consumer."""
    produto_id = produto_id or str(uuid.uuid4())
    sqs_event = {
        "Records": [{
            "body": json.dumps({
                "Message": json.dumps({
                    "evento": "ProdutoCriado",
                    "dados": {
                        "produto_id": produto_id,
                        "sku": sku,
                        "nome": nome,
                        "categoria_nome": "Categoria Teste",
                    },
                })
            })
        }]
    }
    event_consumer.handler(sqs_event, None)

    # Find the created item id
    resp = estoque.handler(
        {"httpMethod": "GET", "path": f"/api/v1/estoque/produto/{produto_id}"},
        None,
    )
    body = json.loads(resp["body"])
    item_id = body["id"]

    if not ativo:
        # Desativar via evento
        deactivate_event = {
            "Records": [{
                "body": json.dumps({
                    "Message": json.dumps({
                        "evento": "ProdutoDesativado",
                        "dados": {"produto_id": produto_id},
                    })
                })
            }]
        }
        event_consumer.handler(deactivate_event, None)

    return item_id, produto_id


def _call(method, path, body=None):
    event = {"httpMethod": method, "path": path}
    if body is not None:
        event["body"] = json.dumps(body)
    resp = estoque.handler(event, None)
    return resp["statusCode"], json.loads(resp["body"])


# ---------------------------------------------------------------------------
# Entrada (4)
# ---------------------------------------------------------------------------
def test_registrar_entrada():
    """POST entrada → 201 + movimentacao ENTRADA."""
    item_id, _ = _create_item()
    status, data = _call("POST", f"/api/v1/estoque/{item_id}/entrada",
                         {"quantidade": 100, "lote": "NF-001", "motivo": "Recebimento"})
    assert status == 201
    assert data["tipo"] == "ENTRADA"
    assert data["quantidade"] == 100


def test_saldo_apos_entrada():
    """Entrada 100 + 50 → saldo=150."""
    item_id, _ = _create_item()
    _call("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 100})
    _call("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 50})
    status, data = _call("GET", f"/api/v1/estoque/{item_id}")
    assert status == 200
    assert data["saldo"] == 150


def test_entrada_quantidade_invalida():
    """quantidade=0 → 422."""
    item_id, _ = _create_item()
    status, _ = _call("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 0})
    assert status == 422


def test_entrada_item_inexistente():
    """uuid aleatorio → 404."""
    status, _ = _call("POST", f"/api/v1/estoque/{uuid.uuid4()}/entrada", {"quantidade": 10})
    assert status == 404


# ---------------------------------------------------------------------------
# Consultas (3)
# ---------------------------------------------------------------------------
def test_listar_itens_estoque():
    """Criar 2 → GET → lista com 2+."""
    _create_item(sku="SKU-A", nome="A")
    _create_item(sku="SKU-B", nome="B")
    status, data = _call("GET", "/api/v1/estoque")
    assert status == 200
    assert len(data) >= 2


def test_buscar_item_por_produto():
    """GET /produto/{id} → 200."""
    _, produto_id = _create_item()
    status, data = _call("GET", f"/api/v1/estoque/produto/{produto_id}")
    assert status == 200
    assert data["produto_id"] == produto_id


def test_historico_movimentacoes():
    """3 entradas → GET movimentacoes → 3."""
    item_id, _ = _create_item()
    for _ in range(3):
        _call("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 10})
    status, data = _call("GET", f"/api/v1/estoque/{item_id}/movimentacoes")
    assert status == 200
    assert len(data) == 3


# ---------------------------------------------------------------------------
# Saida (4)
# ---------------------------------------------------------------------------
def test_registrar_saida():
    """Entrada 100 + saida 30 → saldo=70."""
    item_id, _ = _create_item()
    _call("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 100})
    status, data = _call("POST", f"/api/v1/estoque/{item_id}/saida",
                         {"quantidade": 30, "motivo": "Venda"})
    assert status == 201
    _, item = _call("GET", f"/api/v1/estoque/{item_id}")
    assert item["saldo"] == 70


def test_saida_estoque_insuficiente():
    """Entrada 10 + saida 20 → 422."""
    item_id, _ = _create_item()
    _call("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 10})
    status, _ = _call("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 20})
    assert status == 422


def test_saida_zera_estoque():
    """Entrada 50 + saida 50 → saldo=0."""
    item_id, _ = _create_item()
    _call("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 50})
    _call("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 50})
    _, item = _call("GET", f"/api/v1/estoque/{item_id}")
    assert item["saldo"] == 0


def test_multiplas_movimentacoes():
    """Entrada 100, saida 30, saida 30 → saldo=40."""
    item_id, _ = _create_item()
    _call("POST", f"/api/v1/estoque/{item_id}/entrada", {"quantidade": 100})
    _call("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 30})
    _call("POST", f"/api/v1/estoque/{item_id}/saida", {"quantidade": 30})
    _, item = _call("GET", f"/api/v1/estoque/{item_id}")
    assert item["saldo"] == 40
    _, movs = _call("GET", f"/api/v1/estoque/{item_id}/movimentacoes")
    assert len(movs) == 3


# ---------------------------------------------------------------------------
# Eventos (3)
# ---------------------------------------------------------------------------
def test_evento_produto_criado_cria_item():
    """Simular SQS event → item criado com saldo=0."""
    produto_id = str(uuid.uuid4())
    sqs_event = {
        "Records": [{
            "body": json.dumps({
                "Message": json.dumps({
                    "evento": "ProdutoCriado",
                    "dados": {
                        "produto_id": produto_id,
                        "sku": "EVT-001",
                        "nome": "Produto Evento",
                        "categoria_nome": "Cat Evento",
                    },
                })
            })
        }]
    }
    event_consumer.handler(sqs_event, None)
    status, data = _call("GET", f"/api/v1/estoque/produto/{produto_id}")
    assert status == 200
    assert data["saldo"] == 0
    assert data["produto_id"] == produto_id


def test_evento_idempotente():
    """Mesmo evento 2x → apenas 1 item."""
    produto_id = str(uuid.uuid4())
    sqs_event = {
        "Records": [{
            "body": json.dumps({
                "Message": json.dumps({
                    "evento": "ProdutoCriado",
                    "dados": {
                        "produto_id": produto_id,
                        "sku": "IDEMP-001",
                        "nome": "Idempotente",
                        "categoria_nome": "Cat",
                    },
                })
            })
        }]
    }
    event_consumer.handler(sqs_event, None)
    event_consumer.handler(sqs_event, None)

    # Listar todos e filtrar por produto_id
    status, data = _call("GET", "/api/v1/estoque")
    matching = [i for i in data if i["produto_id"] == produto_id]
    assert len(matching) == 1


def test_evento_produto_atualizado():
    """Atualizar projecao local."""
    produto_id = str(uuid.uuid4())
    # Criar primeiro
    create_event = {
        "Records": [{
            "body": json.dumps({
                "Message": json.dumps({
                    "evento": "ProdutoCriado",
                    "dados": {
                        "produto_id": produto_id,
                        "sku": "UPD-001",
                        "nome": "Nome Original",
                        "categoria_nome": "Cat Original",
                    },
                })
            })
        }]
    }
    event_consumer.handler(create_event, None)

    # Atualizar
    update_event = {
        "Records": [{
            "body": json.dumps({
                "Message": json.dumps({
                    "evento": "ProdutoAtualizado",
                    "dados": {
                        "produto_id": produto_id,
                        "nome": "Nome Atualizado",
                        "categoria_nome": "Cat Atualizada",
                    },
                })
            })
        }]
    }
    event_consumer.handler(update_event, None)

    status, data = _call("GET", f"/api/v1/estoque/produto/{produto_id}")
    assert status == 200
    assert data["nome_produto"] == "Nome Atualizado"
    assert data["categoria_nome"] == "Cat Atualizada"
