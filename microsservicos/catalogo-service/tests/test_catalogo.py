"""Testes de comportamento do Catalogo Service.
Identicos entre DDD e MVC — mesmos payloads, mesmas respostas.
Invoca Lambda handler com event mockado."""
import json
import uuid

from src.handlers.catalogo import handler


def _event(method: str, path: str, body: dict = None, query: dict = None) -> dict:
    event = {
        "httpMethod": method,
        "path": path,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body) if body else None,
        "queryStringParameters": query,
        "requestContext": {"authorizer": {"principalId": "test-user"}},
    }
    return event


def _unique(prefix=""):
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# === Categorias ===

def test_criar_categoria():
    """POST /api/v1/categorias → 201 + id, nome, criado_em."""
    resp = handler(_event("POST", "/api/v1/categorias", {"nome": _unique("Cat-"), "descricao": "Desc"}), None)
    assert resp["statusCode"] == 201
    body = json.loads(resp["body"])
    assert "id" in body
    assert "nome" in body
    assert "criado_em" in body


def test_criar_categoria_duplicada():
    """POST mesmo nome → 409."""
    nome = _unique("Dup-")
    handler(_event("POST", "/api/v1/categorias", {"nome": nome}), None)
    resp = handler(_event("POST", "/api/v1/categorias", {"nome": nome}), None)
    assert resp["statusCode"] == 409


def test_listar_categorias():
    """Criar 2 → GET → lista."""
    for _ in range(2):
        handler(_event("POST", "/api/v1/categorias", {"nome": _unique("Lst-")}), None)
    resp = handler(_event("GET", "/api/v1/categorias"), None)
    assert resp["statusCode"] == 200
    assert len(json.loads(resp["body"])) >= 2


def test_buscar_categoria_por_id():
    """Criar → GET /{id} → 200."""
    created = json.loads(handler(_event("POST", "/api/v1/categorias", {"nome": _unique("Fnd-")}), None)["body"])
    resp = handler(_event("GET", f"/api/v1/categorias/{created['id']}"), None)
    assert resp["statusCode"] == 200
    assert json.loads(resp["body"])["id"] == created["id"]


def test_buscar_categoria_inexistente():
    """GET /{uuid} → 404."""
    resp = handler(_event("GET", f"/api/v1/categorias/{uuid.uuid4()}"), None)
    assert resp["statusCode"] == 404


# === Produtos ===

def _criar_categoria():
    resp = handler(_event("POST", "/api/v1/categorias", {"nome": _unique("PC-")}), None)
    return json.loads(resp["body"])["id"]


def test_criar_produto():
    """POST /api/v1/produtos → 201 + sku, nome, preco."""
    cat_id = _criar_categoria()
    resp = handler(_event("POST", "/api/v1/produtos", {
        "sku": _unique("SKU-"), "nome": "Teclado", "preco": 299.90, "categoria_id": cat_id,
    }), None)
    assert resp["statusCode"] == 201
    body = json.loads(resp["body"])
    assert "id" in body
    assert body["ativo"] is True


def test_criar_produto_sku_duplicado():
    """POST mesmo SKU → 409."""
    cat_id = _criar_categoria()
    sku = _unique("DUP-")
    handler(_event("POST", "/api/v1/produtos", {"sku": sku, "nome": "P1", "preco": 10, "categoria_id": cat_id}), None)
    resp = handler(_event("POST", "/api/v1/produtos", {"sku": sku, "nome": "P2", "preco": 20, "categoria_id": cat_id}), None)
    assert resp["statusCode"] == 409


def test_criar_produto_preco_invalido():
    """POST preco=0 → 422."""
    cat_id = _criar_categoria()
    resp = handler(_event("POST", "/api/v1/produtos", {
        "sku": _unique("PRC-"), "nome": "Bad", "preco": 0, "categoria_id": cat_id,
    }), None)
    assert resp["statusCode"] == 422


def test_criar_produto_categoria_inexistente():
    """POST cat_id invalido → 404."""
    resp = handler(_event("POST", "/api/v1/produtos", {
        "sku": _unique("CAT-"), "nome": "Bad", "preco": 10, "categoria_id": str(uuid.uuid4()),
    }), None)
    assert resp["statusCode"] == 404


def test_listar_produtos():
    """Criar 3 → GET → lista."""
    cat_id = _criar_categoria()
    for i in range(3):
        handler(_event("POST", "/api/v1/produtos", {
            "sku": _unique("LST-"), "nome": f"P{i}", "preco": 10, "categoria_id": cat_id,
        }), None)
    resp = handler(_event("GET", "/api/v1/produtos"), None)
    assert resp["statusCode"] == 200
    assert len(json.loads(resp["body"])) >= 3


def test_listar_produtos_filtro_categoria():
    """Filtrar por categoria_id."""
    cat_a = _criar_categoria()
    cat_b = _criar_categoria()
    for _ in range(2):
        handler(_event("POST", "/api/v1/produtos", {
            "sku": _unique("FA-"), "nome": "A", "preco": 10, "categoria_id": cat_a,
        }), None)
    handler(_event("POST", "/api/v1/produtos", {
        "sku": _unique("FB-"), "nome": "B", "preco": 10, "categoria_id": cat_b,
    }), None)
    resp = handler(_event("GET", "/api/v1/produtos", query={"categoria_id": cat_a}), None)
    assert resp["statusCode"] == 200
    assert len(json.loads(resp["body"])) >= 2


def test_buscar_produto_por_id():
    """Criar → GET /{id} → 200."""
    cat_id = _criar_categoria()
    created = json.loads(handler(_event("POST", "/api/v1/produtos", {
        "sku": _unique("FND-"), "nome": "Find", "preco": 10, "categoria_id": cat_id,
    }), None)["body"])
    resp = handler(_event("GET", f"/api/v1/produtos/{created['id']}"), None)
    assert resp["statusCode"] == 200


def test_atualizar_produto():
    """Criar → PUT /{id} → 200 + dados atualizados."""
    cat_id = _criar_categoria()
    created = json.loads(handler(_event("POST", "/api/v1/produtos", {
        "sku": _unique("UPD-"), "nome": "Old", "preco": 10, "categoria_id": cat_id,
    }), None)["body"])
    resp = handler(_event("PUT", f"/api/v1/produtos/{created['id']}", {"nome": "New", "preco": 99.99}), None)
    assert resp["statusCode"] == 200
    assert json.loads(resp["body"])["nome"] == "New"


def test_desativar_produto():
    """Criar → PATCH /{id}/desativar → 200 + ativo=false."""
    cat_id = _criar_categoria()
    created = json.loads(handler(_event("POST", "/api/v1/produtos", {
        "sku": _unique("DES-"), "nome": "Deactivate", "preco": 10, "categoria_id": cat_id,
    }), None)["body"])
    resp = handler(_event("PATCH", f"/api/v1/produtos/{created['id']}/desativar"), None)
    assert resp["statusCode"] == 200
    assert json.loads(resp["body"])["ativo"] is False
