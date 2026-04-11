from datetime import datetime
from uuid import UUID

import boto3

from src.domain.entities import Categoria
from src.domain.repositories import CategoriaRepository


class DynamoDBCategoriaRepository(CategoriaRepository):
    def __init__(self, table_name: str) -> None:
        self._table_name = table_name
        self._table = None

    def _get_table(self):
        if self._table is None:
            self._table = boto3.resource("dynamodb").Table(self._table_name)
        return self._table

    @staticmethod
    def _to_item(c: Categoria) -> dict:
        return {
            "id": str(c.id),
            "nome": c.nome,
            "descricao": c.descricao or "",
            "criado_em": c.criado_em.isoformat(),
            "atualizado_em": c.atualizado_em.isoformat(),
        }

    @staticmethod
    def _from_item(item: dict) -> Categoria:
        return Categoria(
            id=UUID(item["id"]),
            nome=item["nome"],
            descricao=item.get("descricao") or None,
            criado_em=datetime.fromisoformat(item["criado_em"]),
            atualizado_em=datetime.fromisoformat(item["atualizado_em"]),
        )

    def get_by_id(self, entity_id: UUID) -> Categoria | None:
        resp = self._get_table().get_item(Key={"id": str(entity_id)})
        item = resp.get("Item")
        return self._from_item(item) if item else None

    def get_by_nome(self, nome: str) -> Categoria | None:
        resp = self._get_table().scan(
            FilterExpression="#n = :nome",
            ExpressionAttributeNames={"#n": "nome"},
            ExpressionAttributeValues={":nome": nome},
        )
        items = resp.get("Items", [])
        return self._from_item(items[0]) if items else None

    def list_all(self) -> list[Categoria]:
        resp = self._get_table().scan()
        return [self._from_item(i) for i in resp.get("Items", [])]

    def save(self, entity: Categoria) -> Categoria:
        self._get_table().put_item(Item=self._to_item(entity))
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._get_table().delete_item(Key={"id": str(entity_id)})
