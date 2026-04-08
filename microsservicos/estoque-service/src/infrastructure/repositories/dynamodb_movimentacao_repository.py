from datetime import datetime
from uuid import UUID

import boto3

from src.domain.entities.movimentacao import Movimentacao
from src.domain.repositories.movimentacao_repository import MovimentacaoRepository
from src.domain.value_objects.tipo_movimentacao import TipoMovimentacao


class DynamoDBMovimentacaoRepository(MovimentacaoRepository):
    def __init__(self, table_name: str, endpoint_url: str | None = None) -> None:
        kwargs = {}
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        self._table = boto3.resource("dynamodb", **kwargs).Table(table_name)

    def save(self, entity: Movimentacao) -> Movimentacao:
        self._table.put_item(Item={
            "id": str(entity.id),
            "item_estoque_id": str(entity.item_estoque_id),
            "tipo": entity.tipo.value,
            "quantidade": entity.quantidade,
            "lote": entity.lote,
            "motivo": entity.motivo,
            "criado_em": entity.criado_em.isoformat(),
            "atualizado_em": entity.atualizado_em.isoformat(),
        })
        return entity

    def list_by_item(
        self,
        item_estoque_id: UUID,
        tipo: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Movimentacao]:
        filters = ["item_estoque_id = :item_id"]
        values = {":item_id": str(item_estoque_id)}

        if tipo is not None:
            filters.append("tipo = :tipo")
            values[":tipo"] = tipo

        response = self._table.scan(
            FilterExpression=" AND ".join(filters),
            ExpressionAttributeValues=values,
        )
        items = response.get("Items", [])

        movimentacoes = [self._to_domain(item) for item in items]
        start = (page - 1) * size
        return movimentacoes[start : start + size]

    @staticmethod
    def _to_domain(item: dict) -> Movimentacao:
        return Movimentacao(
            id=UUID(item["id"]),
            item_estoque_id=UUID(item["item_estoque_id"]),
            tipo=TipoMovimentacao(item["tipo"]),
            quantidade=int(item["quantidade"]),
            lote=item.get("lote"),
            motivo=item.get("motivo"),
            criado_em=datetime.fromisoformat(item["criado_em"]),
            atualizado_em=datetime.fromisoformat(item["atualizado_em"]),
        )
