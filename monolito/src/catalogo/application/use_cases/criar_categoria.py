from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from src.catalogo.domain.entities.categoria import Categoria
from src.catalogo.domain.exceptions.catalogo import CategoriaNomeDuplicado
from src.catalogo.domain.repositories.categoria_repository import CategoriaRepository


@dataclass
class CriarCategoriaDTO:
    nome: str
    descricao: str = ""


class CriarCategoriaUseCase:
    def __init__(self, repo: CategoriaRepository) -> None:
        self.repo = repo

    def execute(self, dados: CriarCategoriaDTO) -> Categoria:
        existente = self.repo.get_by_nome(dados.nome)
        if existente is not None:
            raise CategoriaNomeDuplicado()

        categoria = Categoria(
            id=uuid4(),
            nome=dados.nome,
            descricao=dados.descricao,
            criado_em=datetime.now(timezone.utc),
            atualizado_em=datetime.now(timezone.utc),
        )
        return self.repo.save(categoria)
