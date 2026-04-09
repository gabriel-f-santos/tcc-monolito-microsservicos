import json
from src.handlers.health import handler


def test_health_returns_200():
    response = handler({}, None)
    assert response["statusCode"] == 200


def test_health_body():
    body = json.loads(handler({}, None)["body"])
    assert body["status"] == "healthy"
    assert body["service"] == "estoque"
