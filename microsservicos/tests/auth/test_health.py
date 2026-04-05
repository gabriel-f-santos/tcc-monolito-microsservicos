import json
import importlib


def _invoke(module_path, event=None):
    mod = importlib.import_module(module_path)
    return mod.handler(event or {}, None)


def test_auth_health_returns_200():
    response = _invoke("auth-service.src.presentation.handlers.health")
    assert response["statusCode"] == 200


def test_auth_health_body():
    response = _invoke("auth-service.src.presentation.handlers.health")
    body = json.loads(response["body"])
    assert body["status"] == "healthy"
    assert body["service"] == "auth"
