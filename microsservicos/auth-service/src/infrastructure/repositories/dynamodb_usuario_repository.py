from datetime import datetime, timezone
from uuid import UUID

import boto3

from src.domain.entities.usuario import Usuario
from src.domain.repositories.usuario_repository import UsuarioRepository


class DynamoDBUsuarioRepository(UsuarioRepository):
    def __init__(self, table_name: str, endpoint_url: str | None = None) -> None:
        kwargs = {}
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        self._table = boto3.resource("dynamodb", **kwargs).Table(table_name)

    def get_by_id(self, entity_id: UUID) -> Usuario | None:
        response = self._table.get_item(Key={"id": str(entity_id)})
        item = response.get("Item")
        return self._to_domain(item) if item else None

    def get_by_email(self, email: str) -> Usuario | None:
        response = self._table.scan(
            FilterExpression="email = :email",
            ExpressionAttributeValues={":email": email},
        )
        items = response.get("Items", [])
        return self._to_domain(items[0]) if items else None

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
    def _to_domain(item: dict) -> Usuario:
        return Usuario(
            id=UUID(item["id"]),
            nome=item["nome"],
            email=item["email"],
            senha_hash=item["senha_hash"],
            criado_em=datetime.fromisoformat(item["criado_em"]),
            atualizado_em=datetime.fromisoformat(item["atualizado_em"]),
        )
