"""Testes catalogo handler — fake DynamoDB e fake SNS in-memory."""
import json
import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


# --- Fake DynamoDB Table ---

class FakeTable:
    def __init__(self):
        self.items = {}

    def put_item(self, Item):
        self.items[Item["id"]] = {**Item}

    def get_item(self, Key):
        item = self.items.get(Key["id"])
        if item:
            return {"Item": {**item}}
        return {}

    def scan(self, **kwargs):
        items = list(self.items.values())
        filter_expr = kwargs.get("FilterExpression", "")
        expr_values = kwargs.get("ExpressionAttributeValues", {})

        if filter_expr and expr_values:
            filtered = []
            for item in items:
                match = True
                for part in filter_expr.split(" AND "):
                    part = part.strip()
                    field, placeholder = part.split(" = ")
                    field = field.strip()
                    placeholder = placeholder.strip()
                    expected = expr_values[placeholder]
                    val = item.get(field)
                    if val != expected:
                        match = False
                        break
                if match:
                    filtered.append(item)
            return {"Items": filtered}
        return {"Items": items}

    def update_item(self, Key, UpdateExpression, ExpressionAttributeValues):
        item = self.items.get(Key["id"])
        if not item:
            return
        # Parse SET expressions
        set_part = UpdateExpression.replace("SET ", "")
        for assignment in set_part.split(", "):
            field, placeholder = assignment.split(" = ")
            field = field.strip()
            placeholder = placeholder.strip()
            item[field] = ExpressionAttributeValues[placeholder]


# --- Fixtures ---

@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv("CATEGORIAS_TABLE", "tcc-categorias")
    monkeypatch.setenv("PRODUTOS_TABLE", "tcc-produtos")
    monkeypatch.setenv("EVENTOS_TOPIC_ARN", "arn:aws:sns:us-east-1:000:tcc-eventos")


@pytest.fixture
def fake_tables():
    return {"tcc-categorias": FakeTable(), "tcc-produtos": FakeTable()}


@pytest.fixture(autouse=True)
def mock_aws(fake_tables):
    fake_resource = MagicMock()
    fake_resource.Table = lambda name: fake_tables[name]

    fake_sns = MagicMock()

    with patch("src.handlers.catalogo.dynamodb", fake_resource), \
         patch("src.handlers.catalogo.sns", fake_sns):
        yield fake_sns


def _event(method, path, body=None, params=None):
    ev = {"httpMethod": method, "path": path, "queryStringParameters": params}
    if body:
        ev["body"] = json.dumps(body)
    return ev


def _call(method, path, body=None, params=None):
    from src.handlers.catalogo import handler
    resp = handler(_event(method, path, body, params), None)
    return resp["statusCode"], json.loads(resp["body"])


# ==================== Categorias ====================

def test_criar_categoria():
    status, body = _call("POST", "/api/v1/categorias", {"nome": "Eletronicos"})
    assert status == 201
    assert body["nome"] == "Eletronicos"
    assert "id" in body
    assert "criado_em" in body


def test_criar_categoria_duplicada():
    _call("POST", "/api/v1/categorias", {"nome": "Alimentos"})
    status, body = _call("POST", "/api/v1/categorias", {"nome": "Alimentos"})
    assert status == 409


def test_listar_categorias():
    _call("POST", "/api/v1/categorias", {"nome": "Cat A"})
    _call("POST", "/api/v1/categorias", {"nome": "Cat B"})
    status, body = _call("GET", "/api/v1/categorias")
    assert status == 200
    assert len(body) >= 2


def test_buscar_categoria_por_id():
    _, cat = _call("POST", "/api/v1/categorias", {"nome": "Busca Cat"})
    status, body = _call("GET", f"/api/v1/categorias/{cat['id']}")
    assert status == 200
    assert body["nome"] == "Busca Cat"


def test_buscar_categoria_inexistente():
    fake_id = str(uuid.uuid4())
    status, body = _call("GET", f"/api/v1/categorias/{fake_id}")
    assert status == 404


# ==================== Produtos ====================

def _criar_cat_e_produto(nome_cat="Geral", sku="SKU-001", nome="Produto 1", preco=29.90):
    _, cat = _call("POST", "/api/v1/categorias", {"nome": nome_cat})
    status, prod = _call("POST", "/api/v1/produtos", {
        "sku": sku, "nome": nome, "preco": preco, "categoria_id": cat["id"],
    })
    return cat, status, prod


def test_criar_produto():
    cat, status, prod = _criar_cat_e_produto()
    assert status == 201
    assert prod["sku"] == "SKU-001"
    assert prod["nome"] == "Produto 1"
    assert prod["preco"] == 29.90
    assert prod["categoria"]["id"] == cat["id"]


def test_criar_produto_sku_duplicado():
    _criar_cat_e_produto(nome_cat="Dup Cat", sku="SKU-DUP")
    _, cat2 = _call("POST", "/api/v1/categorias", {"nome": "Dup Cat 2"})
    status, _ = _call("POST", "/api/v1/produtos", {
        "sku": "SKU-DUP", "nome": "Outro", "preco": 10, "categoria_id": cat2["id"],
    })
    assert status == 409


def test_criar_produto_preco_invalido():
    _, cat = _call("POST", "/api/v1/categorias", {"nome": "Preco Cat"})
    status, _ = _call("POST", "/api/v1/produtos", {
        "sku": "SKU-X", "nome": "Prod", "preco": 0, "categoria_id": cat["id"],
    })
    assert status == 422


def test_criar_produto_categoria_inexistente():
    fake_id = str(uuid.uuid4())
    status, _ = _call("POST", "/api/v1/produtos", {
        "sku": "SKU-Y", "nome": "Prod", "preco": 10, "categoria_id": fake_id,
    })
    assert status == 404


def test_listar_produtos():
    _, cat = _call("POST", "/api/v1/categorias", {"nome": "List Cat"})
    for i in range(3):
        _call("POST", "/api/v1/produtos", {
            "sku": f"LST-{i}", "nome": f"Prod {i}", "preco": 10 + i, "categoria_id": cat["id"],
        })
    status, body = _call("GET", "/api/v1/produtos")
    assert status == 200
    assert len(body) >= 3


def test_listar_produtos_filtro_categoria():
    _, cat1 = _call("POST", "/api/v1/categorias", {"nome": "Filtro A"})
    _, cat2 = _call("POST", "/api/v1/categorias", {"nome": "Filtro B"})
    _call("POST", "/api/v1/produtos", {"sku": "FA-1", "nome": "P1", "preco": 5, "categoria_id": cat1["id"]})
    _call("POST", "/api/v1/produtos", {"sku": "FB-1", "nome": "P2", "preco": 5, "categoria_id": cat2["id"]})
    status, body = _call("GET", "/api/v1/produtos", params={"categoria_id": cat1["id"]})
    assert status == 200
    assert all(p["categoria"]["id"] == cat1["id"] for p in body)


def test_buscar_produto_por_id():
    _, _, prod = _criar_cat_e_produto(nome_cat="Busca P Cat", sku="BP-1")
    status, body = _call("GET", f"/api/v1/produtos/{prod['id']}")
    assert status == 200
    assert body["sku"] == "BP-1"


def test_atualizar_produto():
    _, _, prod = _criar_cat_e_produto(nome_cat="Upd Cat", sku="UPD-1")
    status, body = _call("PUT", f"/api/v1/produtos/{prod['id']}", {
        "nome": "Atualizado", "preco": 99.99,
    })
    assert status == 200
    assert body["nome"] == "Atualizado"
    assert body["preco"] == 99.99


def test_desativar_produto():
    _, _, prod = _criar_cat_e_produto(nome_cat="Des Cat", sku="DES-1")
    status, body = _call("PATCH", f"/api/v1/produtos/{prod['id']}/desativar")
    assert status == 200
    assert body["ativo"] is False
