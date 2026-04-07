import json
from src.presentation.handlers.event_consumer import handler


def test_event_consumer_handles_empty_records():
    response = handler({"Records": []}, None)
    assert response["statusCode"] == 200


def test_event_consumer_processes_produto_criado():
    sns_message = json.dumps({
        "evento": "ProdutoCriado",
        "dados": {"produto_id": "abc-123", "sku": "ELET-001"},
    })
    event = {
        "Records": [
            {"body": json.dumps({"Message": sns_message})}
        ]
    }
    response = handler(event, None)
    assert response["statusCode"] == 200
