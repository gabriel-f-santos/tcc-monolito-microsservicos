from __future__ import annotations

from datetime import datetime
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Attr

from src.domain.entities.alerta_estoque import AlertaEstoque
from src.domain.repositories.alerta_estoque_repository import AlertaEstoqueRepository


class DynamoDBAlertaEstoqueRepository(AlertaEstoqueRepository):
    def __init__(self, table_name: str) -> None:
        self._table_name = table_name

    @property
    def _table(self):
        return boto3.resource("dynamodb").Table(self._table_name)

    def _to_entity(self, row: dict) -> AlertaEstoque:
        return AlertaEstoque(
            id=UUID(row["id"]),
            item_estoque_id=UUID(row["item_estoque_id"]),
            tipo=row["tipo"],
            saldo_atual=int(row["saldo_atual"]),
            estoque_minimo=int(row["estoque_minimo"]),
            criado_em=datetime.fromisoformat(row["criado_em"]),
            atualizado_em=datetime.fromisoformat(row["atualizado_em"]),
        )

    def _to_row(self, entity: AlertaEstoque) -> dict:
        return {
            "id": str(entity.id),
            "item_estoque_id": str(entity.item_estoque_id),
            "tipo": entity.tipo,
            "saldo_atual": int(entity.saldo_atual),
            "estoque_minimo": int(entity.estoque_minimo),
            "criado_em": entity.criado_em.isoformat(),
            "atualizado_em": entity.atualizado_em.isoformat(),
        }

    def get_by_id(self, entity_id: UUID) -> AlertaEstoque | None:
        resp = self._table.get_item(Key={"id": str(entity_id)})
        row = resp.get("Item")
        if row is None:
            return None
        return self._to_entity(row)

    def list_by_item(self, item_estoque_id: UUID) -> list[AlertaEstoque]:
        resp = self._table.scan(
            FilterExpression=Attr("item_estoque_id").eq(str(item_estoque_id))
        )
        rows = resp.get("Items", [])
        rows.sort(key=lambda r: r.get("criado_em", ""))
        return [self._to_entity(r) for r in rows]

    def save(self, entity: AlertaEstoque) -> AlertaEstoque:
        self._table.put_item(Item=self._to_row(entity))
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._table.delete_item(Key={"id": str(entity_id)})
