"""Tests para auth handlers — fake DynamoDB in-memory."""
import json

import pytest

from src.handlers import auth
from src.handlers.auth import registrar_handler, login_handler
from src.handlers.authorizer import handler as authorizer_handler


# ── Fake DynamoDB table (in-memory) ──────────────────────────────


class FakeTable:
    def __init__(self):
        self.items = []

    def scan(self, **kwargs):
        fe = kwargs.get("FilterExpression")
        if fe is not None:
            matched = [i for i in self.items if self._match(i, fe)]
            return {"Items": matched}
        return {"Items": list(self.items)}

    def put_item(self, **kwargs):
        self.items.append(kwargs["Item"])

    @staticmethod
    def _match(item, fe):
        # fe is a boto3 ConditionExpression; in tests it's always Attr("email").eq(value)
        expr = fe.get_expression()
        key = expr["values"][0].name
        value = expr["values"][1]
        return item.get(key) == value


_fake_table = FakeTable()


@pytest.fixture(autouse=True)
def _reset_table(monkeypatch):
    global _fake_table
    _fake_table = FakeTable()
    monkeypatch.setattr(auth, "_table", None)
    monkeypatch.setattr(auth, "_get_table", lambda: _fake_table)


def _event(body: dict) -> dict:
    return {"body": json.dumps(body)}


# ── Tests ────────────────────────────────────────────────────────


def test_registrar_sucesso():
    resp = registrar_handler(_event({"nome": "Admin", "email": "admin@test.com", "senha": "senha12345"}), None)
    assert resp["statusCode"] == 201
    body = json.loads(resp["body"])
    assert body["id"]
    assert body["nome"] == "Admin"
    assert body["email"] == "admin@test.com"
    assert body["criado_em"]
    assert "senha" not in body and "senha_hash" not in body


def test_registrar_email_duplicado():
    registrar_handler(_event({"nome": "Admin", "email": "admin@test.com", "senha": "senha12345"}), None)
    resp = registrar_handler(_event({"nome": "Admin2", "email": "admin@test.com", "senha": "outra123"}), None)
    assert resp["statusCode"] == 409


def test_login_sucesso():
    registrar_handler(_event({"nome": "Admin", "email": "admin@test.com", "senha": "senha12345"}), None)
    resp = login_handler(_event({"email": "admin@test.com", "senha": "senha12345"}), None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_senha_errada():
    registrar_handler(_event({"nome": "Admin", "email": "admin@test.com", "senha": "senha12345"}), None)
    resp = login_handler(_event({"email": "admin@test.com", "senha": "errada"}), None)
    assert resp["statusCode"] == 401


def test_authorizer_token_valido():
    registrar_handler(_event({"nome": "Admin", "email": "admin@test.com", "senha": "senha12345"}), None)
    login_resp = login_handler(_event({"email": "admin@test.com", "senha": "senha12345"}), None)
    token = json.loads(login_resp["body"])["access_token"]

    event = {
        "authorizationToken": f"Bearer {token}",
        "methodArn": "arn:aws:execute-api:us-east-1:123456:apiid/prod/GET/resource",
    }
    policy = authorizer_handler(event, None)
    assert policy["policyDocument"]["Statement"][0]["Effect"] == "Allow"
    assert "/*" in policy["policyDocument"]["Statement"][0]["Resource"]


def test_authorizer_token_invalido():
    event = {
        "authorizationToken": "Bearer lixo",
        "methodArn": "arn:aws:execute-api:us-east-1:123456:apiid/prod/GET/resource",
    }
    with pytest.raises(Exception, match="Unauthorized"):
        authorizer_handler(event, None)
