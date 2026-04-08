"""Categoria tests — mesmos payloads e respostas do monolito DDD."""
import uuid
from tests.conftest import _register_and_login, _auth_header


def test_criar_categoria(client):
    """POST /api/v1/categorias → 201 + categoria com id, nome, descricao, criado_em."""
    token = _register_and_login(client)
    response = client.post("/api/v1/categorias",
        json={"nome": f"Cat-{uuid.uuid4().hex[:6]}", "descricao": "Descricao"},
        headers=_auth_header(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "nome" in data
    assert "criado_em" in data


def test_criar_categoria_duplicada(client):
    """POST duas vezes com mesmo nome → 409."""
    token = _register_and_login(client)
    nome = f"Dup-{uuid.uuid4().hex[:6]}"
    client.post("/api/v1/categorias", json={"nome": nome}, headers=_auth_header(token))
    response = client.post("/api/v1/categorias", json={"nome": nome}, headers=_auth_header(token))
    assert response.status_code == 409


def test_listar_categorias(client):
    """Criar 2 categorias → GET → 200 + lista."""
    token = _register_and_login(client)
    for i in range(2):
        client.post("/api/v1/categorias",
            json={"nome": f"List-{uuid.uuid4().hex[:6]}"},
            headers=_auth_header(token),
        )
    response = client.get("/api/v1/categorias", headers=_auth_header(token))
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 2


def test_buscar_categoria_por_id(client):
    """Criar categoria → GET /{id} → 200."""
    token = _register_and_login(client)
    created = client.post("/api/v1/categorias",
        json={"nome": f"Find-{uuid.uuid4().hex[:6]}"},
        headers=_auth_header(token),
    ).json()
    response = client.get(f"/api/v1/categorias/{created['id']}", headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_buscar_categoria_inexistente(client):
    """GET /{uuid-aleatorio} → 404."""
    token = _register_and_login(client)
    response = client.get(f"/api/v1/categorias/{uuid.uuid4()}", headers=_auth_header(token))
    assert response.status_code == 404
