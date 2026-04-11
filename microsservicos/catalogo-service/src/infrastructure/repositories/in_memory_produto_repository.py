from uuid import UUID

from src.domain.entities.produto import Produto
from src.domain.repositories.produto_repository import ProdutoRepository


class InMemoryProdutoRepository(ProdutoRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Produto] = {}

    def get_by_id(self, entity_id: UUID) -> Produto | None:
        return self._store.get(entity_id)

    def get_by_sku(self, sku: str) -> Produto | None:
        for prod in self._store.values():
            if prod.sku.valor == sku:
                return prod
        return None

    def list_filtered(
        self,
        categoria_id: UUID | None = None,
        ativo: bool | None = None,
    ) -> list[Produto]:
        result = list(self._store.values())
        if categoria_id is not None:
            result = [p for p in result if p.categoria_id == categoria_id]
        if ativo is not None:
            result = [p for p in result if p.ativo == ativo]
        return result

    def save(self, entity: Produto) -> Produto:
        self._store[entity.id] = entity
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._store.pop(entity_id, None)
