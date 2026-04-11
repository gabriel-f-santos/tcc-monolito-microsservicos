from uuid import UUID

from src.domain.entities.categoria import Categoria
from src.domain.repositories.categoria_repository import CategoriaRepository


class InMemoryCategoriaRepository(CategoriaRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Categoria] = {}

    def get_by_id(self, entity_id: UUID) -> Categoria | None:
        return self._store.get(entity_id)

    def get_by_nome(self, nome: str) -> Categoria | None:
        for cat in self._store.values():
            if cat.nome == nome:
                return cat
        return None

    def list_all(self) -> list[Categoria]:
        return list(self._store.values())

    def save(self, entity: Categoria) -> Categoria:
        self._store[entity.id] = entity
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._store.pop(entity_id, None)
