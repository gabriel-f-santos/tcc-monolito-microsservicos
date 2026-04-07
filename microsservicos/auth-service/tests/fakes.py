from uuid import UUID

from src.domain.entities.usuario import Usuario
from src.domain.repositories.usuario_repository import UsuarioRepository


class FakeUsuarioRepository(UsuarioRepository):
    def __init__(self) -> None:
        self._store: dict[str, Usuario] = {}

    def get_by_id(self, entity_id: UUID) -> Usuario | None:
        return self._store.get(str(entity_id))

    def get_by_email(self, email: str) -> Usuario | None:
        for u in self._store.values():
            if u.email == email:
                return u
        return None

    def save(self, entity: Usuario) -> Usuario:
        self._store[str(entity.id)] = entity
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._store.pop(str(entity_id), None)
