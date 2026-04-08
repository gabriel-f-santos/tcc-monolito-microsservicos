"""Auth tests — mesmos payloads e respostas esperadas do monolito DDD."""
import uuid
from tests.conftest import _auth_header


def test_registrar_sucesso(client):
    """POST /api/v1/auth/registrar com dados validos → 201 + usuario sem senha."""
    email = f"reg-{uuid.uuid4().hex[:8]}@test.com"
    response = client.post("/api/v1/auth/registrar", json={
        "nome": "Admin TCC",
        "email": email,
        "senha": "senha12345",
    })
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["nome"] == "Admin TCC"
    assert data["email"] == email
    assert "criado_em" in data
    assert "senha_hash" not in data
    assert "senha" not in data


def test_registrar_email_duplicado(client):
    """POST registrar duas vezes com mesmo email → 409."""
    email = f"dup-{uuid.uuid4().hex[:8]}@test.com"
    client.post("/api/v1/auth/registrar", json={
        "nome": "User 1", "email": email, "senha": "senha12345",
    })
    response = client.post("/api/v1/auth/registrar", json={
        "nome": "User 2", "email": email, "senha": "senha12345",
    })
    assert response.status_code == 409


def test_login_sucesso(client):
    """Registrar → POST /api/v1/auth/login → 200 + access_token."""
    email = f"login-{uuid.uuid4().hex[:8]}@test.com"
    client.post("/api/v1/auth/registrar", json={
        "nome": "Login User", "email": email, "senha": "senha12345",
    })
    response = client.post("/api/v1/auth/login", json={
        "email": email, "senha": "senha12345",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_senha_errada(client):
    """Registrar → login com senha errada → 401."""
    email = f"wrong-{uuid.uuid4().hex[:8]}@test.com"
    client.post("/api/v1/auth/registrar", json={
        "nome": "Wrong Pass", "email": email, "senha": "senha12345",
    })
    response = client.post("/api/v1/auth/login", json={
        "email": email, "senha": "senhaerrada",
    })
    assert response.status_code == 401


def test_rota_protegida_sem_token(client):
    """GET /api/v1/categorias sem header Authorization → 401."""
    response = client.get("/api/v1/categorias")
    assert response.status_code == 401


def test_rota_protegida_com_token(client):
    """Login → GET /api/v1/categorias com Bearer token → nao 401."""
    email = f"prot-{uuid.uuid4().hex[:8]}@test.com"
    client.post("/api/v1/auth/registrar", json={
        "nome": "Protected", "email": email, "senha": "senha12345",
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": email, "senha": "senha12345",
    })
    token = resp.json()["access_token"]
    response = client.get("/api/v1/categorias", headers=_auth_header(token))
    assert response.status_code != 401
