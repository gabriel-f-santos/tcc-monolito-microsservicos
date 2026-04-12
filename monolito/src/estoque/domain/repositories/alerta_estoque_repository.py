from abc import abstractmethod
from uuid import UUID

from src.estoque.domain.entities.alerta_estoque import AlertaEstoque
from src.shared.domain.repositories.base import BaseRepository


class AlertaEstoqueRepository(BaseRepository[AlertaEstoque]):
    @abstractmethod
    def list_by_item(self, item_estoque_id: UUID) -> list[AlertaEstoque]:
        ...
