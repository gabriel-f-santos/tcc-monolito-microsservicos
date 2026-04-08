from datetime import datetime
from decimal import Decimal
from uuid import UUID

import boto3

from src.domain.entities.produto import Produto
from src.domain.repositories.produto_repository import ProdutoRepository
from src.domain.value_objects.dinheiro import Dinheiro
from src.domain.value_objects.sku import SKU


class DynamoDBProdutoRepository(ProdutoRepository):
    def __init__(self, table_name: str, endpoint_url: str | None = None) -> None:
        kwargs = {}
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        self._table = boto3.resource("dynamodb", **kwargs).Table(table_name)

    def get_by_id(self, entity_id: UUID) -> Produto | None:
        response = self._table.get_item(Key={"id": str(entity_id)})
        item = response.get("Item")
        return self._to_domain(item) if item else None

    def get_by_sku(self, sku: str) -> Produto | None:
        response = self._table.scan(
            FilterExpression="sku = :sku",
            ExpressionAttributeValues={":sku": sku},
        )
        items = response.get("Items", [])
        return self._to_domain(items[0]) if items else None

    def list_filtered(
        self,
        categoria_id: UUID | None = None,
        ativo: bool | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Produto]:
        scan_kwargs = {}
        filters = []
        values = {}

        if categoria_id is not None:
            filters.append("categoria_id = :cat_id")
            values[":cat_id"] = str(categoria_id)

        if ativo is not None:
            filters.append("ativo = :ativo")
            values[":ativo"] = ativo

        if filters:
            scan_kwargs["FilterExpression"] = " AND ".join(filters)
            scan_kwargs["ExpressionAttributeValues"] = values

        response = self._table.scan(**scan_kwargs)
        items = response.get("Items", [])

        produtos = [self._to_domain(item) for item in items]
        start = (page - 1) * size
        return produtos[start : start + size]

    def save(self, entity: Produto) -> Produto:
        self._table.put_item(Item={
            "id": str(entity.id),
            "sku": entity.sku.valor,
            "nome": entity.nome,
            "descricao": entity.descricao,
            "preco": str(entity.preco.valor),
            "categoria_id": str(entity.categoria_id),
            "ativo": entity.ativo,
            "criado_em": entity.criado_em.isoformat(),
            "atualizado_em": entity.atualizado_em.isoformat(),
        })
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._table.delete_item(Key={"id": str(entity_id)})

    @staticmethod
    def _to_domain(item: dict) -> Produto:
        return Produto(
            id=UUID(item["id"]),
            sku=SKU(valor=item["sku"]),
            nome=item["nome"],
            descricao=item.get("descricao"),
            preco=Dinheiro(valor=Decimal(item["preco"])),
            categoria_id=UUID(item["categoria_id"]),
            ativo=item.get("ativo", True),
            criado_em=datetime.fromisoformat(item["criado_em"]),
            atualizado_em=datetime.fromisoformat(item["atualizado_em"]),
        )
