from datetime import datetime
from uuid import UUID

import boto3

from src.domain.entities.categoria import Categoria
from src.domain.repositories.categoria_repository import CategoriaRepository


class DynamoDBCategoriaRepository(CategoriaRepository):
    def __init__(self, table_name: str, endpoint_url: str | None = None) -> None:
        kwargs = {}
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        self._table = boto3.resource("dynamodb", **kwargs).Table(table_name)

    def get_by_id(self, entity_id: UUID) -> Categoria | None:
        response = self._table.get_item(Key={"id": str(entity_id)})
        item = response.get("Item")
        return self._to_domain(item) if item else None

    def get_by_nome(self, nome: str) -> Categoria | None:
        response = self._table.scan(
            FilterExpression="nome = :nome",
            ExpressionAttributeValues={":nome": nome},
        )
        items = response.get("Items", [])
        return self._to_domain(items[0]) if items else None

    def list_all(self) -> list[Categoria]:
        response = self._table.scan()
        items = response.get("Items", [])
        return [self._to_domain(item) for item in items]

    def save(self, entity: Categoria) -> Categoria:
        self._table.put_item(Item={
            "id": str(entity.id),
            "nome": entity.nome,
            "descricao": entity.descricao,
            "criado_em": entity.criado_em.isoformat(),
            "atualizado_em": entity.atualizado_em.isoformat(),
        })
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._table.delete_item(Key={"id": str(entity_id)})

    @staticmethod
    def _to_domain(item: dict) -> Categoria:
        return Categoria(
            id=UUID(item["id"]),
            nome=item["nome"],
            descricao=item.get("descricao"),
            criado_em=datetime.fromisoformat(item["criado_em"]),
            atualizado_em=datetime.fromisoformat(item["atualizado_em"]),
        )
