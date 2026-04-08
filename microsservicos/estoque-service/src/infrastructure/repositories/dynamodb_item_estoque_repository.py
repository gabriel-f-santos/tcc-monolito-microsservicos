from datetime import datetime
from uuid import UUID

import boto3

from src.domain.entities.item_estoque import ItemEstoque
from src.domain.repositories.item_estoque_repository import ItemEstoqueRepository


class DynamoDBItemEstoqueRepository(ItemEstoqueRepository):
    def __init__(self, table_name: str, endpoint_url: str | None = None) -> None:
        kwargs = {}
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        self._table = boto3.resource("dynamodb", **kwargs).Table(table_name)

    def get_by_id(self, entity_id: UUID) -> ItemEstoque | None:
        response = self._table.get_item(Key={"id": str(entity_id)})
        item = response.get("Item")
        return self._to_domain(item) if item else None

    def get_by_produto_id(self, produto_id: UUID) -> ItemEstoque | None:
        response = self._table.scan(
            FilterExpression="produto_id = :pid",
            ExpressionAttributeValues={":pid": str(produto_id)},
        )
        items = response.get("Items", [])
        return self._to_domain(items[0]) if items else None

    def list_filtered(
        self,
        saldo_min: int | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[ItemEstoque]:
        scan_kwargs = {}
        filters = []
        values = {}

        if saldo_min is not None:
            filters.append("saldo >= :saldo_min")
            values[":saldo_min"] = saldo_min

        if filters:
            scan_kwargs["FilterExpression"] = " AND ".join(filters)
            scan_kwargs["ExpressionAttributeValues"] = values

        response = self._table.scan(**scan_kwargs)
        items = response.get("Items", [])

        domain_items = [self._to_domain(item) for item in items]
        start = (page - 1) * size
        return domain_items[start : start + size]

    def save(self, entity: ItemEstoque) -> ItemEstoque:
        self._table.put_item(Item={
            "id": str(entity.id),
            "produto_id": str(entity.produto_id),
            "sku": entity.sku,
            "nome_produto": entity.nome_produto,
            "categoria_nome": entity.categoria_nome,
            "saldo": entity.saldo,
            "ativo": entity.ativo,
            "criado_em": entity.criado_em.isoformat(),
            "atualizado_em": entity.atualizado_em.isoformat(),
        })
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._table.delete_item(Key={"id": str(entity_id)})

    @staticmethod
    def _to_domain(item: dict) -> ItemEstoque:
        return ItemEstoque(
            id=UUID(item["id"]),
            produto_id=UUID(item["produto_id"]),
            sku=item["sku"],
            nome_produto=item["nome_produto"],
            categoria_nome=item["categoria_nome"],
            saldo=int(item["saldo"]),
            ativo=item.get("ativo", True),
            criado_em=datetime.fromisoformat(item["criado_em"]),
            atualizado_em=datetime.fromisoformat(item["atualizado_em"]),
        )
