import os
from datetime import datetime, timezone
from uuid import UUID

import boto3

from src.domain.entities.categoria import Categoria
from src.domain.repositories.categoria_repository import CategoriaRepository


class DynamoDBCategoriaRepository(CategoriaRepository):
    def __init__(self) -> None:
        self._table = boto3.resource("dynamodb").Table(
            os.environ["CATEGORIAS_TABLE"]
        )

    def get_by_id(self, entity_id: UUID) -> Categoria | None:
        resp = self._table.get_item(Key={"id": str(entity_id)})
        item = resp.get("Item")
        if item is None:
            return None
        return self._to_entity(item)

    def get_by_nome(self, nome: str) -> Categoria | None:
        resp = self._table.scan(
            FilterExpression="nome = :n",
            ExpressionAttributeValues={":n": nome},
        )
        items = resp.get("Items", [])
        return self._to_entity(items[0]) if items else None

    def list_all(self) -> list[Categoria]:
        resp = self._table.scan()
        return [self._to_entity(item) for item in resp.get("Items", [])]

    def save(self, entity: Categoria) -> Categoria:
        self._table.put_item(Item={
            "id": str(entity.id),
            "nome": entity.nome,
            "descricao": entity.descricao or "",
            "criado_em": entity.criado_em.isoformat(),
            "atualizado_em": entity.atualizado_em.isoformat(),
        })
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._table.delete_item(Key={"id": str(entity_id)})

    @staticmethod
    def _to_entity(item: dict) -> Categoria:
        return Categoria(
            id=UUID(item["id"]),
            nome=item["nome"],
            descricao=item.get("descricao") or None,
            criado_em=datetime.fromisoformat(item["criado_em"]).replace(tzinfo=timezone.utc),
            atualizado_em=datetime.fromisoformat(item["atualizado_em"]).replace(tzinfo=timezone.utc),
        )
