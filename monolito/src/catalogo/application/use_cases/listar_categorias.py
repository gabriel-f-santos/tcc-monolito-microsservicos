from src.catalogo.domain.entities.categoria import Categoria
from src.catalogo.domain.repositories.categoria_repository import CategoriaRepository


class ListarCategoriasUseCase:
    def __init__(self, repo: CategoriaRepository) -> None:
        self.repo = repo

    def execute(self) -> list[Categoria]:
        return self.repo.list_all()
