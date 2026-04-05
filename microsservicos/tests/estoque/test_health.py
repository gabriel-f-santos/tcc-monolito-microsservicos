import json
import importlib


def _invoke(module_path: str, event: dict | None = None):
    """Helper to invoke a Lambda handler."""
    mod = importlib.import_module(module_path)
    return mod.handler(event or {}, None)


def test_estoque_health_returns_200():
    response = _invoke("estoque-service.src.presentation.handlers.health")
    assert response["statusCode"] == 200


def test_estoque_health_body():
    response = _invoke("estoque-service.src.presentation.handlers.health")
    body = json.loads(response["body"])
    assert body["status"] == "healthy"
    assert body["service"] == "estoque"
