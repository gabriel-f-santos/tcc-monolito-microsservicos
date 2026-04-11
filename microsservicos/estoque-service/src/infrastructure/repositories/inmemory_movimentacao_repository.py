from uuid import UUID

from src.domain.entities.movimentacao import Movimentacao
from src.domain.repositories.movimentacao_repository import MovimentacaoRepository


class InMemoryMovimentacaoRepository(MovimentacaoRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Movimentacao] = {}

    def save(self, entity: Movimentacao) -> Movimentacao:
        self._store[entity.id] = entity
        return entity

    def list_by_item(
        self,
        item_estoque_id: UUID,
        tipo: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Movimentacao]:
        items = [m for m in self._store.values() if m.item_estoque_id == item_estoque_id]
        if tipo is not None:
            items = [m for m in items if m.tipo.value == tipo]
        start = (page - 1) * size
        return items[start : start + size]
