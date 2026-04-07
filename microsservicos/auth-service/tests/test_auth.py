import json
from uuid import uuid4

import pytest

from src.container import AuthContainer
from tests.fakes import FakeUsuarioRepository


@pytest.fixture
def container():
    c = AuthContainer(
        table_name="test-usuarios",
        jwt_secret="test-secret",
        jwt_expiration_hours=24,
    )
    c.usuario_repository.override(FakeUsuarioRepository())
    return c


def _make_event(body: dict) -> dict:
    return {"body": json.dumps(body)}


def _unique_email() -> str:
    return f"user-{uuid4().hex[:8]}@test.com"


def _registrar(container, body: dict) -> dict:
    from src.presentation.handlers.auth import registrar_handler, login_handler

    # Temporarily patch module-level container
    import src.presentation.handlers.auth as auth_mod
    original = auth_mod.container
    auth_mod.container = container
    try:
        return registrar_handler(_make_event(body), None)
    finally:
        auth_mod.container = original


def _login(container, body: dict) -> dict:
    import src.presentation.handlers.auth as auth_mod
    original = auth_mod.container
    auth_mod.container = container
    try:
        from src.presentation.handlers.auth import login_handler
        return login_handler(_make_event(body), None)
    finally:
        auth_mod.container = original


def _authorize(container, token: str) -> dict:
    import src.presentation.handlers.authorizer as auth_mod
    original = auth_mod.container
    auth_mod.container = container
    try:
        from src.presentation.handlers.authorizer import handler
        event = {
            "authorizationToken": f"Bearer {token}",
            "methodArn": "arn:aws:execute-api:us-east-1:123456789:api/stage/GET/resource",
        }
        return handler(event, None)
    finally:
        auth_mod.container = original


class TestRegistrar:
    def test_registrar_sucesso(self, container):
        email = _unique_email()
        resp = _registrar(container, {"nome": "Admin", "email": email, "senha": "minimo8chars"})
        assert resp["statusCode"] == 201
        data = json.loads(resp["body"])
        assert "id" in data
        assert data["nome"] == "Admin"
        assert data["email"] == email.lower()
        assert "criado_em" in data

    def test_registrar_email_duplicado(self, container):
        email = _unique_email()
        _registrar(container, {"nome": "Admin", "email": email, "senha": "minimo8chars"})
        resp = _registrar(container, {"nome": "Admin2", "email": email, "senha": "minimo8chars"})
        assert resp["statusCode"] == 409
        data = json.loads(resp["body"])
        assert data["code"] == "EMAIL_DUPLICADO"


class TestLogin:
    def test_login_sucesso(self, container):
        email = _unique_email()
        _registrar(container, {"nome": "Admin", "email": email, "senha": "minimo8chars"})
        resp = _login(container, {"email": email, "senha": "minimo8chars"})
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_senha_errada(self, container):
        email = _unique_email()
        _registrar(container, {"nome": "Admin", "email": email, "senha": "minimo8chars"})
        resp = _login(container, {"email": email, "senha": "senhaerrada"})
        assert resp["statusCode"] == 401
        data = json.loads(resp["body"])
        assert data["code"] == "CREDENCIAIS_INVALIDAS"


class TestAuthorizer:
    def test_authorizer_token_valido(self, container):
        email = _unique_email()
        _registrar(container, {"nome": "Admin", "email": email, "senha": "minimo8chars"})
        login_resp = _login(container, {"email": email, "senha": "minimo8chars"})
        token = json.loads(login_resp["body"])["access_token"]
        result = _authorize(container, token)
        assert result["policyDocument"]["Statement"][0]["Effect"] == "Allow"

    def test_authorizer_token_invalido(self, container):
        with pytest.raises(Exception, match="Unauthorized"):
            _authorize(container, "lixo")
