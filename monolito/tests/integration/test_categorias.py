from uuid import uuid4

from fastapi.testclient import TestClient


def _get_token(client: TestClient) -> str:
    email = f"cat-{uuid4().hex[:8]}@test.com"
    client.post(
        "/api/v1/auth/registrar",
        json={"nome": "Admin", "email": email, "senha": "minimo8chars"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "minimo8chars"},
    )
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_criar_categoria(client: TestClient):
    token = _get_token(client)
    nome = f"Cat-{uuid4().hex[:8]}"
    response = client.post(
        "/api/v1/categorias",
        json={"nome": nome, "descricao": "Produtos eletronicos"},
        headers=_auth_header(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["nome"] == nome
    assert data["descricao"] == "Produtos eletronicos"
    assert "criado_em" in data


def test_criar_categoria_duplicada(client: TestClient):
    token = _get_token(client)
    nome = f"Dup-{uuid4().hex[:8]}"
    client.post(
        "/api/v1/categorias",
        json={"nome": nome, "descricao": ""},
        headers=_auth_header(token),
    )
    response = client.post(
        "/api/v1/categorias",
        json={"nome": nome, "descricao": ""},
        headers=_auth_header(token),
    )
    assert response.status_code == 409
    assert response.json()["code"] == "CATEGORIA_NOME_DUPLICADO"


def test_listar_categorias(client: TestClient):
    token = _get_token(client)
    nome1 = f"List1-{uuid4().hex[:8]}"
    nome2 = f"List2-{uuid4().hex[:8]}"
    client.post(
        "/api/v1/categorias",
        json={"nome": nome1, "descricao": ""},
        headers=_auth_header(token),
    )
    client.post(
        "/api/v1/categorias",
        json={"nome": nome2, "descricao": ""},
        headers=_auth_header(token),
    )
    response = client.get("/api/v1/categorias", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    nomes = [c["nome"] for c in data]
    assert nome1 in nomes
    assert nome2 in nomes


def test_buscar_categoria_por_id(client: TestClient):
    token = _get_token(client)
    nome = f"Busca-{uuid4().hex[:8]}"
    create_resp = client.post(
        "/api/v1/categorias",
        json={"nome": nome, "descricao": "desc"},
        headers=_auth_header(token),
    )
    cat_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/categorias/{cat_id}", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cat_id
    assert data["nome"] == nome
    assert data["descricao"] == "desc"


def test_buscar_categoria_inexistente(client: TestClient):
    token = _get_token(client)
    fake_id = str(uuid4())
    response = client.get(f"/api/v1/categorias/{fake_id}", headers=_auth_header(token))
    assert response.status_code == 404
    assert response.json()["code"] == "CATEGORIA_NAO_ENCONTRADA"
