from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.entities.categoria import Categoria
from src.domain.exceptions.catalogo import CategoriaNomeDuplicado
from src.domain.repositories.categoria_repository import CategoriaRepository


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

        now = datetime.now(timezone.utc)
        categoria = Categoria(
            id=uuid4(),
            nome=dados.nome,
            descricao=dados.descricao,
            criado_em=now,
            atualizado_em=now,
        )
        return self.repo.save(categoria)
