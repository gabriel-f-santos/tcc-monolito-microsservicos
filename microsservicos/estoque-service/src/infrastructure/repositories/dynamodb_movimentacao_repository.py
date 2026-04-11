from __future__ import annotations

from datetime import datetime
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Attr

from src.domain.entities.movimentacao import Movimentacao
from src.domain.repositories.movimentacao_repository import MovimentacaoRepository
from src.domain.value_objects.tipo_movimentacao import TipoMovimentacao


class DynamoDBMovimentacaoRepository(MovimentacaoRepository):
    def __init__(self, table_name: str) -> None:
        self._table_name = table_name

    @property
    def _table(self):
        return boto3.resource("dynamodb").Table(self._table_name)

    def _to_entity(self, row: dict) -> Movimentacao:
        return Movimentacao(
            id=UUID(row["id"]),
            item_estoque_id=UUID(row["item_estoque_id"]),
            tipo=TipoMovimentacao(row["tipo"]),
            quantidade=int(row["quantidade"]),
            lote=row.get("lote"),
            motivo=row.get("motivo"),
            criado_em=datetime.fromisoformat(row["criado_em"]),
            atualizado_em=datetime.fromisoformat(row["atualizado_em"]),
        )

    def _to_row(self, entity: Movimentacao) -> dict:
        return {
            "id": str(entity.id),
            "item_estoque_id": str(entity.item_estoque_id),
            "tipo": entity.tipo.value,
            "quantidade": int(entity.quantidade),
            "lote": entity.lote,
            "motivo": entity.motivo,
            "criado_em": entity.criado_em.isoformat(),
            "atualizado_em": entity.atualizado_em.isoformat(),
        }

    def save(self, entity: Movimentacao) -> Movimentacao:
        self._table.put_item(Item=self._to_row(entity))
        return entity

    def list_by_item(
        self,
        item_estoque_id: UUID,
        tipo: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Movimentacao]:
        filter_expr = Attr("item_estoque_id").eq(str(item_estoque_id))
        if tipo is not None:
            filter_expr = filter_expr & Attr("tipo").eq(tipo)
        resp = self._table.scan(FilterExpression=filter_expr)
        rows = resp.get("Items", [])
        rows.sort(key=lambda r: r.get("criado_em", ""))
        start = max(0, (page - 1) * size)
        end = start + size
        return [self._to_entity(r) for r in rows[start:end]]
