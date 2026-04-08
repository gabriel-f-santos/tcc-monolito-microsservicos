from uuid import UUID

from src.domain.entities.categoria import Categoria
from src.domain.entities.produto import Produto
from src.domain.repositories.categoria_repository import CategoriaRepository
from src.domain.repositories.produto_repository import ProdutoRepository
from src.shared.domain.services.estoque_service import EstoqueService


class FakeProdutoRepository(ProdutoRepository):
    def __init__(self) -> None:
        self._store: dict[str, Produto] = {}

    def get_by_id(self, entity_id: UUID) -> Produto | None:
        return self._store.get(str(entity_id))

    def get_by_sku(self, sku: str) -> Produto | None:
        for p in self._store.values():
            if p.sku.valor == sku:
                return p
        return None

    def list_filtered(
        self,
        categoria_id: UUID | None = None,
        ativo: bool | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Produto]:
        result = list(self._store.values())
        if categoria_id is not None:
            result = [p for p in result if p.categoria_id == categoria_id]
        if ativo is not None:
            result = [p for p in result if p.ativo == ativo]
        start = (page - 1) * size
        return result[start : start + size]

    def save(self, entity: Produto) -> Produto:
        self._store[str(entity.id)] = entity
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._store.pop(str(entity_id), None)


class FakeCategoriaRepository(CategoriaRepository):
    def __init__(self) -> None:
        self._store: dict[str, Categoria] = {}

    def get_by_id(self, entity_id: UUID) -> Categoria | None:
        return self._store.get(str(entity_id))

    def get_by_nome(self, nome: str) -> Categoria | None:
        for c in self._store.values():
            if c.nome == nome:
                return c
        return None

    def list_all(self) -> list[Categoria]:
        return list(self._store.values())

    def save(self, entity: Categoria) -> Categoria:
        self._store[str(entity.id)] = entity
        return entity

    def delete(self, entity_id: UUID) -> None:
        self._store.pop(str(entity_id), None)


class FakeEstoqueService(EstoqueService):
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def inicializar_item(
        self,
        produto_id: UUID,
        sku: str,
        nome_produto: str,
        categoria_nome: str,
    ) -> None:
        self.calls.append({
            "produto_id": produto_id,
            "sku": sku,
            "nome_produto": nome_produto,
            "categoria_nome": categoria_nome,
        })
