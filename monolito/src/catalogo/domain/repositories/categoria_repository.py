from abc import abstractmethod

from src.catalogo.domain.entities.categoria import Categoria
from src.shared.domain.repositories.base import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    @abstractmethod
    def get_by_nome(self, nome: str) -> Categoria | None:
        ...

    @abstractmethod
    def list_all(self) -> list[Categoria]:
        ...
