import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Consome eventos de dominio do Catalogo via SQS."""
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        # SNS wraps the message in a "Message" field
        message = json.loads(body.get("Message", "{}"))
        evento = message.get("evento", "desconhecido")
        logger.info(f"Evento recebido: {evento}")
        # TODO: delegar ao use case apropriado na Fase 5

    return {"statusCode": 200}
