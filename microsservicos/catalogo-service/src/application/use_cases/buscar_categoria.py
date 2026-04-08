from uuid import UUID

from src.domain.entities.categoria import Categoria
from src.domain.exceptions.catalogo import CategoriaNaoEncontrada
from src.domain.repositories.categoria_repository import CategoriaRepository


class BuscarCategoriaUseCase:
    def __init__(self, repo: CategoriaRepository) -> None:
        self.repo = repo

    def execute(self, categoria_id: UUID) -> Categoria:
        categoria = self.repo.get_by_id(categoria_id)
        if categoria is None:
            raise CategoriaNaoEncontrada()
        return categoria
