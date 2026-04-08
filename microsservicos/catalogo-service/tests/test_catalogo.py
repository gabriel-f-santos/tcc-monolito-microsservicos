import json
from uuid import uuid4

import pytest

from src.container import CatalogoContainer
from tests.fakes import FakeCategoriaRepository, FakeEstoqueService, FakeProdutoRepository


@pytest.fixture
def container():
    c = CatalogoContainer(
        produtos_table="test-produtos",
        categorias_table="test-categorias",
        eventos_topic_arn="arn:aws:sns:us-east-1:000000000000:test-topic",
    )
    c.produto_repository.override(FakeProdutoRepository())
    c.categoria_repository.override(FakeCategoriaRepository())
    c.estoque_service.override(FakeEstoqueService())
    return c


def _make_event(
    method: str,
    path: str,
    body: dict | None = None,
    query: dict | None = None,
    user_id: str = "test-user",
) -> dict:
    event = {
        "httpMethod": method,
        "path": path,
        "requestContext": {"authorizer": {"principalId": user_id}},
        "queryStringParameters": query,
    }
    if body is not None:
        event["body"] = json.dumps(body)
    return event


def _call_handler(container, event: dict) -> dict:
    import src.presentation.handlers.catalogo as handler_mod
    original = handler_mod.container
    handler_mod.container = container
    try:
        return handler_mod.handler(event, None)
    finally:
        handler_mod.container = original


def _criar_categoria(container, nome: str = "Eletronicos", descricao: str = "Desc") -> dict:
    event = _make_event("POST", "/catalogo/categorias", {"nome": nome, "descricao": descricao})
    resp = _call_handler(container, event)
    return resp


def _criar_produto(container, categoria_id: str, sku: str = "SKU-001", nome: str = "Produto 1", preco: float = 99.90) -> dict:
    event = _make_event("POST", "/catalogo/produtos", {
        "sku": sku,
        "nome": nome,
        "preco": preco,
        "categoria_id": categoria_id,
    })
    return _call_handler(container, event)


# ============================================================
# Categoria (5 testes)
# ============================================================

class TestCriarCategoria:
    def test_criar_categoria(self, container):
        resp = _criar_categoria(container)
        assert resp["statusCode"] == 201
        data = json.loads(resp["body"])
        assert data["nome"] == "Eletronicos"
        assert "id" in data

    def test_criar_categoria_duplicada(self, container):
        _criar_categoria(container, nome="Roupas")
        resp = _criar_categoria(container, nome="Roupas")
        assert resp["statusCode"] == 409
        data = json.loads(resp["body"])
        assert data["code"] == "CATEGORIA_NOME_DUPLICADO"


class TestListarCategorias:
    def test_listar_categorias(self, container):
        _criar_categoria(container, nome="Cat1")
        _criar_categoria(container, nome="Cat2")
        event = _make_event("GET", "/catalogo/categorias")
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert len(data) == 2


class TestBuscarCategoria:
    def test_buscar_categoria_por_id(self, container):
        create_resp = _criar_categoria(container)
        cat_id = json.loads(create_resp["body"])["id"]
        event = _make_event("GET", f"/catalogo/categorias/{cat_id}")
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert data["id"] == cat_id

    def test_buscar_categoria_inexistente(self, container):
        fake_id = str(uuid4())
        event = _make_event("GET", f"/catalogo/categorias/{fake_id}")
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 404
        data = json.loads(resp["body"])
        assert data["code"] == "CATEGORIA_NAO_ENCONTRADA"


# ============================================================
# Produto (9 testes)
# ============================================================

class TestCriarProduto:
    def test_criar_produto(self, container):
        cat_resp = _criar_categoria(container)
        cat_id = json.loads(cat_resp["body"])["id"]
        resp = _criar_produto(container, cat_id)
        assert resp["statusCode"] == 201
        data = json.loads(resp["body"])
        assert data["sku"] == "SKU-001"
        assert data["nome"] == "Produto 1"
        assert data["ativo"] is True

    def test_criar_produto_sku_duplicado(self, container):
        cat_resp = _criar_categoria(container)
        cat_id = json.loads(cat_resp["body"])["id"]
        _criar_produto(container, cat_id, sku="DUP-001")
        resp = _criar_produto(container, cat_id, sku="DUP-001", nome="Outro")
        assert resp["statusCode"] == 409
        data = json.loads(resp["body"])
        assert data["code"] == "PRODUTO_SKU_DUPLICADO"

    def test_criar_produto_preco_invalido(self, container):
        cat_resp = _criar_categoria(container)
        cat_id = json.loads(cat_resp["body"])["id"]
        resp = _criar_produto(container, cat_id, sku="NEG-001", preco=-10)
        assert resp["statusCode"] == 400
        data = json.loads(resp["body"])
        assert data["code"] == "PRECO_INVALIDO"

    def test_criar_produto_categoria_inexistente(self, container):
        fake_id = str(uuid4())
        resp = _criar_produto(container, fake_id)
        assert resp["statusCode"] == 404
        data = json.loads(resp["body"])
        assert data["code"] == "CATEGORIA_NAO_ENCONTRADA"


class TestListarProdutos:
    def test_listar_produtos(self, container):
        cat_resp = _criar_categoria(container)
        cat_id = json.loads(cat_resp["body"])["id"]
        _criar_produto(container, cat_id, sku="LST-001", nome="P1")
        _criar_produto(container, cat_id, sku="LST-002", nome="P2")
        event = _make_event("GET", "/catalogo/produtos")
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert len(data) == 2

    def test_listar_produtos_filtro_categoria(self, container):
        cat1 = json.loads(_criar_categoria(container, nome="Cat1")["body"])["id"]
        cat2 = json.loads(_criar_categoria(container, nome="Cat2")["body"])["id"]
        _criar_produto(container, cat1, sku="FLT-001", nome="P1")
        _criar_produto(container, cat2, sku="FLT-002", nome="P2")
        event = _make_event("GET", "/catalogo/produtos", query={"categoria_id": cat1})
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert len(data) == 1
        assert data[0]["categoria_id"] == cat1


class TestBuscarProduto:
    def test_buscar_produto_por_id(self, container):
        cat_resp = _criar_categoria(container)
        cat_id = json.loads(cat_resp["body"])["id"]
        prod_resp = _criar_produto(container, cat_id)
        prod_id = json.loads(prod_resp["body"])["id"]
        event = _make_event("GET", f"/catalogo/produtos/{prod_id}")
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert data["id"] == prod_id


class TestAtualizarProduto:
    def test_atualizar_produto(self, container):
        cat_resp = _criar_categoria(container)
        cat_id = json.loads(cat_resp["body"])["id"]
        prod_resp = _criar_produto(container, cat_id)
        prod_id = json.loads(prod_resp["body"])["id"]
        event = _make_event("PUT", f"/catalogo/produtos/{prod_id}", {"nome": "Novo Nome"})
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert data["nome"] == "Novo Nome"


class TestDesativarProduto:
    def test_desativar_produto(self, container):
        cat_resp = _criar_categoria(container)
        cat_id = json.loads(cat_resp["body"])["id"]
        prod_resp = _criar_produto(container, cat_id)
        prod_id = json.loads(prod_resp["body"])["id"]
        event = _make_event("DELETE", f"/catalogo/produtos/{prod_id}")
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert data["ativo"] is False
