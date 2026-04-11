import os
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import boto3

from src.domain.entities.produto import Produto
from src.domain.repositories.produto_repository import ProdutoRepository
from src.domain.value_objects.dinheiro import Dinheiro
from src.domain.value_objects.sku import SKU


class DynamoDBProdutoRepository(ProdutoRepository):
    def __init__(self) -> None:
        self._table = boto3.resource("dynamodb").Table(
            os.environ["PRODUTOS_TABLE"]
        )

    def get_by_id(self, entity_id: UUID) -> Produto | None:
        resp = self._table.get_item(Key={"id": str(entity_id)})
        item = resp.get("Item")
        if item is None:
            return None
        return self._to_entity(item)

    def get_by_sku(self, sku: str) -> Produto | None:
        resp = self._table.scan(
            FilterExpression="sku = :s",
            ExpressionAttributeValues={":s": sku},
        )
        items = resp.get("Items", [])
        return self._to_entity(items[0]) if items else None

    def list_filtered(
        self,
        categoria_id: UUID | None = None,
        ativo: bool | None = None,
    ) -> list[Produto]:
        filter_parts = []
        expr_values = {}
        if categoria_id is not None:
            filter_parts.append("categoria_id = :cid")
            expr_values[":cid"] = str(categoria_id)
        if ativo is not None:
            filter_parts.append("ativo = :a")
            expr_values[":a"] = ativo

        scan_kwargs = {}
        if filter_parts:
            scan_kwargs["FilterExpression"] = " AND ".join(filter_parts)
            scan_kwargs["ExpressionAttributeValues"] = expr_values

        resp = self._table.scan(**scan_kwargs)
        return [self._to_entity(item) for item in resp.get("Items", [])]

    def save(self, entity: Produto) -> Produto:
        self._table.put_item(Item={
            "id": str(entity.id),
            "sku": entity.sku.valor,
            "nome": entity.nome,
            "descricao": entity.descricao or "",
            "preco": entity.preco.valor,
            "categoria_id": str(entity.categoria_id),
            "ativo": entity.ativo,
            "criado_em": entity.criado_em.isoformat(),
            "atualizado_em": entity.atualizado_em.isoformat(),
        })
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._table.delete_item(Key={"id": str(entity_id)})

    @staticmethod
    def _to_entity(item: dict) -> Produto:
        return Produto(
            id=UUID(item["id"]),
            sku=SKU(valor=item["sku"]),
            nome=item["nome"],
            descricao=item.get("descricao") or None,
            preco=Dinheiro(valor=Decimal(str(item["preco"]))),
            categoria_id=UUID(item["categoria_id"]),
            ativo=item.get("ativo", True),
            criado_em=datetime.fromisoformat(item["criado_em"]).replace(tzinfo=timezone.utc),
            atualizado_em=datetime.fromisoformat(item["atualizado_em"]).replace(tzinfo=timezone.utc),
        )
