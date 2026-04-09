"""Testes de comportamento do Auth Service.
Identicos entre DDD e MVC — mesmos payloads, mesmas respostas.
Invoca Lambda handlers com event mockado."""
import json
import uuid

from src.handlers.auth import registrar_handler, login_handler
from src.handlers.authorizer import handler as authorizer_handler


def _event(body: dict, path: str = "", method: str = "POST") -> dict:
    return {
        "httpMethod": method,
        "path": path,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@test.com"


# === Registrar ===

def test_registrar_sucesso():
    """POST registrar com dados validos → 201 + usuario sem senha."""
    event = _event({"nome": "Admin", "email": _unique_email(), "senha": "senha12345"})
    response = registrar_handler(event, None)
    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert "id" in body
    assert body["nome"] == "Admin"
    assert "email" in body
    assert "criado_em" in body
    assert "senha_hash" not in body
    assert "senha" not in body


def test_registrar_email_duplicado():
    """POST registrar duas vezes com mesmo email → 409."""
    email = _unique_email()
    event = _event({"nome": "User", "email": email, "senha": "senha12345"})
    registrar_handler(event, None)
    response = registrar_handler(event, None)
    assert response["statusCode"] == 409


# === Login ===

def test_login_sucesso():
    """Registrar → POST login → 200 + access_token."""
    email = _unique_email()
    registrar_handler(_event({"nome": "Login", "email": email, "senha": "senha12345"}), None)
    response = login_handler(_event({"email": email, "senha": "senha12345"}), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_senha_errada():
    """Registrar → login com senha errada → 401."""
    email = _unique_email()
    registrar_handler(_event({"nome": "Wrong", "email": email, "senha": "senha12345"}), None)
    response = login_handler(_event({"email": email, "senha": "senhaerrada"}), None)
    assert response["statusCode"] == 401


# === Authorizer ===

def test_authorizer_token_valido():
    """Login → authorizer com Bearer token → Allow policy."""
    email = _unique_email()
    registrar_handler(_event({"nome": "Auth", "email": email, "senha": "senha12345"}), None)
    login_resp = login_handler(_event({"email": email, "senha": "senha12345"}), None)
    token = json.loads(login_resp["body"])["access_token"]

    auth_event = {
        "authorizationToken": f"Bearer {token}",
        "methodArn": "arn:aws:execute-api:us-east-1:123456789:abc123/Prod/GET/test",
    }
    policy = authorizer_handler(auth_event, None)
    assert policy["policyDocument"]["Statement"][0]["Effect"] == "Allow"


def test_authorizer_token_invalido():
    """Authorizer com token invalido → Unauthorized."""
    auth_event = {
        "authorizationToken": "Bearer token-invalido",
        "methodArn": "arn:aws:execute-api:us-east-1:123456789:abc123/Prod/GET/test",
    }
    try:
        authorizer_handler(auth_event, None)
        assert False, "Deveria ter lancado Exception"
    except Exception as e:
        assert "Unauthorized" in str(e)
