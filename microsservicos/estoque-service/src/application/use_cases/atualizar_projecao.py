from datetime import datetime, timezone
from uuid import UUID

from src.domain.repositories.item_estoque_repository import ItemEstoqueRepository


class AtualizarProjecaoUseCase:
    def __init__(self, repo: ItemEstoqueRepository) -> None:
        self.repo = repo

    def execute(self, dados: dict) -> None:
        produto_id = UUID(dados["produto_id"])
        item = self.repo.get_by_produto_id(produto_id)
        if item is None:
            return

        item.nome_produto = dados.get("nome", item.nome_produto)
        item.categoria_nome = dados.get("categoria_nome", item.categoria_nome)
        item.atualizado_em = datetime.now(timezone.utc)
        self.repo.save(item)
