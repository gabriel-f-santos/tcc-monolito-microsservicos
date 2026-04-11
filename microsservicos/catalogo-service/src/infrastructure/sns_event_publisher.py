import json
from uuid import UUID

import boto3

from src.domain.services import EventPublisher


class SnsEventPublisher(EventPublisher):
    def __init__(self, topic_arn: str) -> None:
        self._topic_arn = topic_arn
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = boto3.client("sns")
        return self._client

    def publicar_produto_criado(
        self,
        produto_id: UUID,
        sku: str,
        nome: str,
        categoria_nome: str,
    ) -> None:
        message = {
            "evento": "ProdutoCriado",
            "dados": {
                "produto_id": str(produto_id),
                "sku": sku,
                "nome": nome,
                "categoria_nome": categoria_nome,
            },
        }
        self._get_client().publish(
            TopicArn=self._topic_arn,
            Message=json.dumps(message),
        )
