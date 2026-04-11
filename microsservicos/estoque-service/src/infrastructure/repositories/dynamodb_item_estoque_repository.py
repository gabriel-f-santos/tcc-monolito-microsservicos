from __future__ import annotations

from datetime import datetime
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Attr

from src.domain.entities.item_estoque import ItemEstoque
from src.domain.repositories.item_estoque_repository import ItemEstoqueRepository


class DynamoDBItemEstoqueRepository(ItemEstoqueRepository):
    def __init__(self, table_name: str) -> None:
        self._table_name = table_name

    @property
    def _table(self):
        return boto3.resource("dynamodb").Table(self._table_name)

    def _to_item(self, row: dict) -> ItemEstoque:
        return ItemEstoque(
            id=UUID(row["id"]),
            produto_id=UUID(row["produto_id"]),
            sku=row["sku"],
            nome_produto=row["nome_produto"],
            categoria_nome=row["categoria_nome"],
            saldo=int(row.get("saldo", 0)),
            ativo=bool(row.get("ativo", True)),
            criado_em=datetime.fromisoformat(row["criado_em"]),
            atualizado_em=datetime.fromisoformat(row["atualizado_em"]),
        )

    def _to_row(self, entity: ItemEstoque) -> dict:
        return {
            "id": str(entity.id),
            "produto_id": str(entity.produto_id),
            "sku": entity.sku,
            "nome_produto": entity.nome_produto,
            "categoria_nome": entity.categoria_nome,
            "saldo": int(entity.saldo),
            "ativo": bool(entity.ativo),
            "criado_em": entity.criado_em.isoformat(),
            "atualizado_em": entity.atualizado_em.isoformat(),
        }

    def get_by_id(self, entity_id: UUID) -> ItemEstoque | None:
        resp = self._table.get_item(Key={"id": str(entity_id)})
        row = resp.get("Item")
        if row is None:
            return None
        return self._to_item(row)

    def get_by_produto_id(self, produto_id: UUID) -> ItemEstoque | None:
        resp = self._table.scan(
            FilterExpression=Attr("produto_id").eq(str(produto_id))
        )
        items = resp.get("Items", [])
        if not items:
            return None
        return self._to_item(items[0])

    def list_filtered(
        self,
        saldo_min: int | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[ItemEstoque]:
        kwargs = {}
        if saldo_min is not None:
            kwargs["FilterExpression"] = Attr("saldo").gte(int(saldo_min))
        resp = self._table.scan(**kwargs)
        rows = resp.get("Items", [])
        start = max(0, (page - 1) * size)
        end = start + size
        return [self._to_item(r) for r in rows[start:end]]

    def save(self, entity: ItemEstoque) -> ItemEstoque:
        self._table.put_item(Item=self._to_row(entity))
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._table.delete_item(Key={"id": str(entity_id)})
