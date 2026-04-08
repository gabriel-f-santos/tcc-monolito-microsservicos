import json
import logging

from src.container import EstoqueContainer
from src.infrastructure.config.settings import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

container = EstoqueContainer(
    itens_estoque_table=settings.itens_estoque_table,
    movimentacoes_table=settings.movimentacoes_table,
)


def handler(event, context):
    """Consome eventos de dominio do Catalogo via SQS."""
    for record in event.get("Records", []):
        try:
            body = json.loads(record["body"])
            message = json.loads(body.get("Message", "{}"))
            evento = message.get("evento", "desconhecido")
            logger.info(f"Evento recebido: {evento}")

            if evento == "ProdutoCriado":
                use_case = container.criar_item_estoque()
                use_case.execute(message["dados"])

            elif evento == "ProdutoAtualizado":
                use_case = container.atualizar_projecao()
                use_case.execute(message["dados"])

            elif evento == "ProdutoDesativado":
                dados = message["dados"]
                from uuid import UUID
                from src.domain.repositories.item_estoque_repository import ItemEstoqueRepository
                repo = container.item_estoque_repository()
                item = repo.get_by_produto_id(UUID(dados["produto_id"]))
                if item is not None:
                    from datetime import datetime, timezone
                    item.ativo = False
                    item.atualizado_em = datetime.now(timezone.utc)
                    repo.save(item)

            else:
                logger.warning(f"Evento desconhecido ignorado: {evento}")

        except Exception:
            logger.exception("Erro ao processar evento SQS")

    return {"statusCode": 200}
