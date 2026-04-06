from fastapi.testclient import TestClient
from uuid import uuid4


def _unique_email() -> str:
    return f"user-{uuid4().hex[:8]}@test.com"


def test_registrar_sucesso(client: TestClient):
    email = _unique_email()
    response = client.post(
        "/api/v1/auth/registrar",
        json={"nome": "Admin", "email": email, "senha": "minimo8chars"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["nome"] == "Admin"
    assert data["email"] == email.lower()
    assert "criado_em" in data
    assert "senha_hash" not in data


def test_registrar_email_duplicado(client: TestClient):
    email = _unique_email()
    client.post(
        "/api/v1/auth/registrar",
        json={"nome": "Admin", "email": email, "senha": "minimo8chars"},
    )
    response = client.post(
        "/api/v1/auth/registrar",
        json={"nome": "Admin2", "email": email, "senha": "minimo8chars"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_DUPLICADO"


def test_login_sucesso(client: TestClient):
    email = _unique_email()
    client.post(
        "/api/v1/auth/registrar",
        json={"nome": "Admin", "email": email, "senha": "minimo8chars"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "minimo8chars"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_senha_errada(client: TestClient):
    email = _unique_email()
    client.post(
        "/api/v1/auth/registrar",
        json={"nome": "Admin", "email": email, "senha": "minimo8chars"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "senhaerrada"},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "CREDENCIAIS_INVALIDAS"


def test_rota_protegida_sem_token(client: TestClient):
    response = client.get("/api/v1/categorias")
    assert response.status_code == 401


def test_rota_protegida_com_token(client: TestClient):
    email = _unique_email()
    client.post(
        "/api/v1/auth/registrar",
        json={"nome": "Admin", "email": email, "senha": "minimo8chars"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "minimo8chars"},
    )
    token = login_resp.json()["access_token"]
    response = client.get(
        "/api/v1/categorias",
        headers={"Authorization": f"Bearer {token}"},
    )
    # Should NOT be 401 — route may not exist (404) but auth should pass
    assert response.status_code != 401
