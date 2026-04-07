import json

import pytest

from src.domain.entities.usuario import Usuario
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.container import AuthContainer


class InMemoryUsuarioRepository(UsuarioRepository):
    def __init__(self):
        self._store: dict[str, Usuario] = {}

    def get_by_id(self, entity_id):
        return self._store.get(str(entity_id))

    def get_by_email(self, email: str):
        for u in self._store.values():
            if u.email == email:
                return u
        return None

    def save(self, entity):
        self._store[str(entity.id)] = entity
        return entity

    def delete(self, entity_id):
        self._store.pop(str(entity_id), None)


@pytest.fixture()
def container():
    c = AuthContainer(
        usuarios_table="test-table",
        jwt_secret="test-secret-key-for-jwt",
        jwt_expiration_hours=24,
    )
    fake_repo = InMemoryUsuarioRepository()
    c.usuario_repository.override(fake_repo)
    yield c
    c.usuario_repository.reset_override()


def _patch_container(module, c):
    """Swap the module-level container and return a cleanup function."""
    original = module.container
    module.container = c
    return lambda: setattr(module, "container", original)


def _registrar_event(nome="Test User", email="test@example.com", senha="Senha123!"):
    return {"body": json.dumps({"nome": nome, "email": email, "senha": senha})}


def _login_event(email="test@example.com", senha="Senha123!"):
    return {"body": json.dumps({"email": email, "senha": senha})}


# ---------- Registrar ----------

def test_registrar_sucesso(container):
    from src.presentation.handlers import auth as mod
    cleanup = _patch_container(mod, container)
    try:
        response = mod.registrar_handler(_registrar_event(), None)
        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["nome"] == "Test User"
        assert body["email"] == "test@example.com"
        assert "id" in body
    finally:
        cleanup()


def test_registrar_email_duplicado(container):
    from src.presentation.handlers import auth as mod
    cleanup = _patch_container(mod, container)
    try:
        mod.registrar_handler(_registrar_event(), None)
        response = mod.registrar_handler(_registrar_event(), None)
        assert response["statusCode"] == 409
        body = json.loads(response["body"])
        assert body["code"] == "EMAIL_DUPLICADO"
    finally:
        cleanup()


# ---------- Login ----------

def test_login_sucesso(container):
    from src.presentation.handlers import auth as mod
    cleanup = _patch_container(mod, container)
    try:
        mod.registrar_handler(_registrar_event(), None)
        response = mod.login_handler(_login_event(), None)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "access_token" in body
        assert body["token_type"] == "bearer"
    finally:
        cleanup()


def test_login_senha_errada(container):
    from src.presentation.handlers import auth as mod
    cleanup = _patch_container(mod, container)
    try:
        mod.registrar_handler(_registrar_event(), None)
        response = mod.login_handler(_login_event(senha="SenhaErrada!"), None)
        assert response["statusCode"] == 401
        body = json.loads(response["body"])
        assert body["code"] == "CREDENCIAIS_INVALIDAS"
    finally:
        cleanup()


# ---------- Authorizer ----------

def test_authorizer_token_valido(container):
    from src.presentation.handlers import auth as auth_mod
    from src.presentation.handlers import authorizer as authz_mod
    cleanup_auth = _patch_container(auth_mod, container)
    cleanup_authz = _patch_container(authz_mod, container)
    try:
        auth_mod.registrar_handler(_registrar_event(), None)
        login_resp = auth_mod.login_handler(_login_event(), None)
        token = json.loads(login_resp["body"])["access_token"]

        event = {
            "authorizationToken": f"Bearer {token}",
            "methodArn": "arn:aws:execute-api:us-east-1:123456:api/Prod/GET/resource",
        }
        policy = authz_mod.handler(event, None)
        assert policy["policyDocument"]["Statement"][0]["Effect"] == "Allow"
        assert "principalId" in policy
    finally:
        cleanup_auth()
        cleanup_authz()


def test_authorizer_token_invalido(container):
    from src.presentation.handlers import authorizer as authz_mod
    cleanup = _patch_container(authz_mod, container)
    try:
        event = {
            "authorizationToken": "Bearer lixo",
            "methodArn": "arn:aws:execute-api:us-east-1:123456:api/Prod/GET/resource",
        }
        with pytest.raises(Exception, match="Unauthorized"):
            authz_mod.handler(event, None)
    finally:
        cleanup()
