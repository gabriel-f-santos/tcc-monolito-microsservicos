import json
from src.presentation.handlers.health import handler


def test_estoque_health_returns_200():
    response = handler({}, None)
    assert response["statusCode"] == 200


def test_estoque_health_body():
    response = handler({}, None)
    body = json.loads(response["body"])
    assert body["status"] == "healthy"
    assert body["service"] == "estoque"
