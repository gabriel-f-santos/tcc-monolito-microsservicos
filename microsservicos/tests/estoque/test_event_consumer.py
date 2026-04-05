import json
import importlib


def test_event_consumer_handles_empty_records():
    mod = importlib.import_module(
        "estoque-service.src.presentation.handlers.event_consumer"
    )
    response = mod.handler({"Records": []}, None)
    assert response["statusCode"] == 200


def test_event_consumer_processes_produto_criado():
    mod = importlib.import_module(
        "estoque-service.src.presentation.handlers.event_consumer"
    )
    sns_message = json.dumps({
        "evento": "ProdutoCriado",
        "dados": {"produto_id": "abc-123", "sku": "ELET-001"},
    })
    event = {
        "Records": [
            {"body": json.dumps({"Message": sns_message})}
        ]
    }
    response = mod.handler(event, None)
    assert response["statusCode"] == 200
