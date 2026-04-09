import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        message = json.loads(body.get("Message", "{}"))
        logger.info(f"Evento: {message.get('evento', 'desconhecido')}")
    return {"statusCode": 200}
