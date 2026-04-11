from datetime import datetime
from decimal import Decimal
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Attr

from src.domain.entities import Produto
from src.domain.repositories import ProdutoRepository
from src.domain.value_objects import Dinheiro, SKU


class DynamoDBProdutoRepository(ProdutoRepository):
    def __init__(self, table_name: str) -> None:
        self._table_name = table_name
        self._table = None

    def _get_table(self):
        if self._table is None:
            self._table = boto3.resource("dynamodb").Table(self._table_name)
        return self._table

    @staticmethod
    def _to_item(p: Produto) -> dict:
        return {
            "id": str(p.id),
            "sku": p.sku.valor,
            "nome": p.nome,
            "descricao": p.descricao or "",
            "preco": str(p.preco.valor),
            "categoria_id": str(p.categoria_id),
            "ativo": p.ativo,
            "criado_em": p.criado_em.isoformat(),
            "atualizado_em": p.atualizado_em.isoformat(),
        }

    @staticmethod
    def _from_item(item: dict) -> Produto:
        return Produto(
            id=UUID(item["id"]),
            sku=SKU(valor=item["sku"]),
            nome=item["nome"],
            descricao=item.get("descricao") or None,
            preco=Dinheiro(valor=Decimal(str(item["preco"]))),
            categoria_id=UUID(item["categoria_id"]),
            ativo=bool(item["ativo"]),
            criado_em=datetime.fromisoformat(item["criado_em"]),
            atualizado_em=datetime.fromisoformat(item["atualizado_em"]),
        )

    def get_by_id(self, entity_id: UUID) -> Produto | None:
        resp = self._get_table().get_item(Key={"id": str(entity_id)})
        item = resp.get("Item")
        return self._from_item(item) if item else None

    def get_by_sku(self, sku: str) -> Produto | None:
        resp = self._get_table().scan(
            FilterExpression=Attr("sku").eq(sku),
        )
        items = resp.get("Items", [])
        return self._from_item(items[0]) if items else None

    def list_filtered(
        self,
        categoria_id: UUID | None = None,
        ativo: bool | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Produto]:
        scan_kwargs: dict = {}
        filter_expr = None
        if categoria_id is not None:
            filter_expr = Attr("categoria_id").eq(str(categoria_id))
        if ativo is not None:
            cond = Attr("ativo").eq(ativo)
            filter_expr = cond if filter_expr is None else filter_expr & cond
        if filter_expr is not None:
            scan_kwargs["FilterExpression"] = filter_expr
        resp = self._get_table().scan(**scan_kwargs)
        items = [self._from_item(i) for i in resp.get("Items", [])]
        start = (page - 1) * size
        return items[start : start + size]

    def save(self, entity: Produto) -> Produto:
        self._get_table().put_item(Item=self._to_item(entity))
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._get_table().delete_item(Key={"id": str(entity_id)})
