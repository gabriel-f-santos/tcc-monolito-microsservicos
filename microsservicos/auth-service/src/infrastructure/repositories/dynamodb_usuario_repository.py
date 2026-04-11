from datetime import datetime, timezone
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Attr

from src.domain.entities.usuario import Usuario
from src.domain.repositories.usuario_repository import UsuarioRepository


class DynamoDBUsuarioRepository(UsuarioRepository):
    def __init__(self, table_name: str, region_name: str = "us-east-1") -> None:
        self._table_name = table_name
        self._region_name = region_name

    def _table(self):
        # Lazy para evitar chamadas AWS em import-time (Regra 5).
        return boto3.resource("dynamodb", region_name=self._region_name).Table(
            self._table_name
        )

    @staticmethod
    def _to_item(usuario: Usuario) -> dict:
        return {
            "id": str(usuario.id),
            "nome": usuario.nome,
            "email": usuario.email,
            "senha_hash": usuario.senha_hash,
            "criado_em": usuario.criado_em.isoformat(),
            "atualizado_em": usuario.atualizado_em.isoformat(),
        }

    @staticmethod
    def _from_item(item: dict) -> Usuario:
        return Usuario(
            id=UUID(item["id"]),
            nome=item["nome"],
            email=item["email"],
            senha_hash=item["senha_hash"],
            criado_em=datetime.fromisoformat(item["criado_em"]),
            atualizado_em=datetime.fromisoformat(item["atualizado_em"]),
        )

    def get_by_id(self, entity_id: UUID) -> Usuario | None:
        resp = self._table().get_item(Key={"id": str(entity_id)})
        item = resp.get("Item")
        if not item:
            return None
        return self._from_item(item)

    def get_by_email(self, email: str) -> Usuario | None:
        resp = self._table().scan(
            FilterExpression=Attr("email").eq(email.lower())
        )
        items = resp.get("Items", [])
        if not items:
            return None
        return self._from_item(items[0])

    def save(self, entity: Usuario) -> Usuario:
        entity.atualizado_em = datetime.now(timezone.utc)
        self._table().put_item(Item=self._to_item(entity))
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._table().delete_item(Key={"id": str(entity_id)})
