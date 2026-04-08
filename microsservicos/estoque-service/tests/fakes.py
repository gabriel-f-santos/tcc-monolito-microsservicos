from uuid import UUID

from src.domain.entities.item_estoque import ItemEstoque
from src.domain.entities.movimentacao import Movimentacao
from src.domain.repositories.item_estoque_repository import ItemEstoqueRepository
from src.domain.repositories.movimentacao_repository import MovimentacaoRepository


class FakeItemEstoqueRepository(ItemEstoqueRepository):
    def __init__(self) -> None:
        self._store: dict[str, ItemEstoque] = {}

    def get_by_id(self, entity_id: UUID) -> ItemEstoque | None:
        return self._store.get(str(entity_id))

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
        result = list(self._store.values())
        if saldo_min is not None:
            result = [i for i in result if i.saldo >= saldo_min]
        start = (page - 1) * size
        return result[start : start + size]

    def save(self, entity: ItemEstoque) -> ItemEstoque:
        self._store[str(entity.id)] = entity
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._store.pop(str(entity_id), None)


class FakeMovimentacaoRepository(MovimentacaoRepository):
    def __init__(self) -> None:
        self._store: list[Movimentacao] = []

    def save(self, entity: Movimentacao) -> Movimentacao:
        self._store.append(entity)
        return entity

    def list_by_item(
        self,
        item_estoque_id: UUID,
        tipo: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Movimentacao]:
        result = [m for m in self._store if m.item_estoque_id == item_estoque_id]
        if tipo is not None:
            result = [m for m in result if m.tipo.value == tipo]
        start = (page - 1) * size
        return result[start : start + size]
