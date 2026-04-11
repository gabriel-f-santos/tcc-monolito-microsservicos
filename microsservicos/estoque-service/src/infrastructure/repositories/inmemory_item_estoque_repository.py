from uuid import UUID

from src.domain.entities.item_estoque import ItemEstoque
from src.domain.repositories.item_estoque_repository import ItemEstoqueRepository


class InMemoryItemEstoqueRepository(ItemEstoqueRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, ItemEstoque] = {}

    def get_by_id(self, entity_id: UUID) -> ItemEstoque | None:
        return self._store.get(entity_id)

    def save(self, entity: ItemEstoque) -> ItemEstoque:
        self._store[entity.id] = entity
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._store.pop(entity_id, None)

    def get_by_produto_id(self, produto_id: UUID) -> ItemEstoque | None:
        for item in self._store.values():
            if item.produto_id == produto_id:
                return item
        return None

    def list_filtered(
        self,
        saldo_min: int | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[ItemEstoque]:
        items = list(self._store.values())
        if saldo_min is not None:
            items = [i for i in items if i.saldo >= saldo_min]
        start = (page - 1) * size
        return items[start : start + size]
