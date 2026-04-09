"""Produto tests — mesmos payloads e respostas do monolito DDD."""
import uuid
from tests.conftest import _register_and_login, _auth_header


def _criar_categoria(client, token):
    resp = client.post("/api/v1/categorias",
        json={"nome": f"ProdCat-{uuid.uuid4().hex[:6]}"},
        headers=_auth_header(token),
    )
    return resp.json()["id"]


def test_criar_produto(client):
    """POST /api/v1/produtos → 201 + produto com categoria nested."""
    token = _register_and_login(client)
    cat_id = _criar_categoria(client, token)
    response = client.post("/api/v1/produtos",
        json={"sku": f"SKU-{uuid.uuid4().hex[:6]}", "nome": "Teclado", "preco": 299.90, "categoria_id": cat_id},
        headers=_auth_header(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["sku"].startswith("SKU-")
    assert data["ativo"] is True
    assert "categoria" in data


def test_criar_produto_sku_duplicado(client):
    """POST dois produtos com mesmo SKU → 409."""
    token = _register_and_login(client)
    cat_id = _criar_categoria(client, token)
    sku = f"DUP-{uuid.uuid4().hex[:6]}"
    client.post("/api/v1/produtos",
        json={"sku": sku, "nome": "P1", "preco": 10, "categoria_id": cat_id},
        headers=_auth_header(token),
    )
    response = client.post("/api/v1/produtos",
        json={"sku": sku, "nome": "P2", "preco": 20, "categoria_id": cat_id},
        headers=_auth_header(token),
    )
    assert response.status_code == 409


def test_criar_produto_preco_invalido(client):
    """POST com preco=0 → 422."""
    token = _register_and_login(client)
    cat_id = _criar_categoria(client, token)
    response = client.post("/api/v1/produtos",
        json={"sku": f"PRC-{uuid.uuid4().hex[:6]}", "nome": "Bad", "preco": 0, "categoria_id": cat_id},
        headers=_auth_header(token),
    )
    assert response.status_code == 422


def test_criar_produto_categoria_inexistente(client):
    """POST com categoria_id invalido → 404."""
    token = _register_and_login(client)
    response = client.post("/api/v1/produtos",
        json={"sku": f"CAT-{uuid.uuid4().hex[:6]}", "nome": "Bad", "preco": 10, "categoria_id": str(uuid.uuid4())},
        headers=_auth_header(token),
    )
    assert response.status_code == 404


def test_listar_produtos(client):
    """Criar 3 produtos → GET → 200 + lista."""
    token = _register_and_login(client)
    cat_id = _criar_categoria(client, token)
    for i in range(3):
        client.post("/api/v1/produtos",
            json={"sku": f"LST-{uuid.uuid4().hex[:6]}", "nome": f"P{i}", "preco": 10, "categoria_id": cat_id},
            headers=_auth_header(token),
        )
    response = client.get("/api/v1/produtos", headers=_auth_header(token))
    assert response.status_code == 200
    assert len(response.json()) >= 3


def test_listar_produtos_filtro_categoria(client):
    """Criar 2 categorias, 3 produtos → filtrar por categoria → retorna correto."""
    token = _register_and_login(client)
    cat_a = _criar_categoria(client, token)
    cat_b = _criar_categoria(client, token)
    for i in range(2):
        client.post("/api/v1/produtos",
            json={"sku": f"FA-{uuid.uuid4().hex[:6]}", "nome": f"A{i}", "preco": 10, "categoria_id": cat_a},
            headers=_auth_header(token),
        )
    client.post("/api/v1/produtos",
        json={"sku": f"FB-{uuid.uuid4().hex[:6]}", "nome": "B0", "preco": 10, "categoria_id": cat_b},
        headers=_auth_header(token),
    )
    response = client.get(f"/api/v1/produtos?categoria_id={cat_a}", headers=_auth_header(token))
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_buscar_produto_por_id(client):
    """Criar produto → GET /{id} → 200."""
    token = _register_and_login(client)
    cat_id = _criar_categoria(client, token)
    created = client.post("/api/v1/produtos",
        json={"sku": f"FND-{uuid.uuid4().hex[:6]}", "nome": "Find", "preco": 10, "categoria_id": cat_id},
        headers=_auth_header(token),
    ).json()
    response = client.get(f"/api/v1/produtos/{created['id']}", headers=_auth_header(token))
    assert response.status_code == 200


def test_atualizar_produto(client):
    """Criar produto → PUT /{id} → 200 + dados atualizados."""
    token = _register_and_login(client)
    cat_id = _criar_categoria(client, token)
    created = client.post("/api/v1/produtos",
        json={"sku": f"UPD-{uuid.uuid4().hex[:6]}", "nome": "Old", "preco": 10, "categoria_id": cat_id},
        headers=_auth_header(token),
    ).json()
    response = client.put(f"/api/v1/produtos/{created['id']}",
        json={"nome": "New Name", "preco": 99.99},
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    assert response.json()["nome"] == "New Name"


def test_desativar_produto(client):
    """Criar produto → PATCH /{id}/desativar → 200 + ativo=false."""
    token = _register_and_login(client)
    cat_id = _criar_categoria(client, token)
    created = client.post("/api/v1/produtos",
        json={"sku": f"DES-{uuid.uuid4().hex[:6]}", "nome": "Deactivate", "preco": 10, "categoria_id": cat_id},
        headers=_auth_header(token),
    ).json()
    response = client.patch(f"/api/v1/produtos/{created['id']}/desativar", headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["ativo"] is False
