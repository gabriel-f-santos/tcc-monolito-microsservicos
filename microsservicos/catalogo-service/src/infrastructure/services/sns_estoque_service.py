import json
from uuid import UUID

import boto3

from src.shared.domain.services.estoque_service import EstoqueService


class SNSEstoqueService(EstoqueService):
    def __init__(self, topic_arn: str) -> None:
        self.sns = boto3.client("sns")
        self.topic_arn = topic_arn

    def inicializar_item(
        self,
        produto_id: UUID,
        sku: str,
        nome_produto: str,
        categoria_nome: str,
    ) -> None:
        self.sns.publish(
            TopicArn=self.topic_arn,
            Message=json.dumps({
                "evento": "ProdutoCriado",
                "dados": {
                    "produto_id": str(produto_id),
                    "sku": sku,
                    "nome": nome_produto,
                    "categoria_nome": categoria_nome,
                },
            }),
        )
