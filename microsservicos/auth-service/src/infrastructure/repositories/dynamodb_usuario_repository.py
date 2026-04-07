from datetime import datetime, timezone
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Attr

from src.domain.entities.usuario import Usuario
from src.domain.repositories.usuario_repository import UsuarioRepository


class DynamoDBUsuarioRepository(UsuarioRepository):
    def __init__(self, table_name: str) -> None:
        dynamodb = boto3.resource("dynamodb")
        self._table = dynamodb.Table(table_name)

    def get_by_id(self, entity_id: UUID) -> Usuario | None:
        response = self._table.get_item(Key={"id": str(entity_id)})
        item = response.get("Item")
        if item is None:
            return None
        return self._to_entity(item)

    def get_by_email(self, email: str) -> Usuario | None:
        response = self._table.scan(
            FilterExpression=Attr("email").eq(email)
        )
        items = response.get("Items", [])
        if not items:
            return None
        return self._to_entity(items[0])

    def save(self, entity: Usuario) -> Usuario:
        self._table.put_item(Item={
            "id": str(entity.id),
            "nome": entity.nome,
            "email": entity.email,
            "senha_hash": entity.senha_hash,
            "criado_em": entity.criado_em.isoformat(),
            "atualizado_em": entity.atualizado_em.isoformat(),
        })
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._table.delete_item(Key={"id": str(entity_id)})

    @staticmethod
    def _to_entity(item: dict) -> Usuario:
        return Usuario(
            id=UUID(item["id"]),
            nome=item["nome"],
            email=item["email"],
            senha_hash=item["senha_hash"],
            criado_em=datetime.fromisoformat(item["criado_em"]),
            atualizado_em=datetime.fromisoformat(item["atualizado_em"]),
        )
