from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.catalogo.domain.services.estoque_service import EstoqueService
from src.estoque.domain.entities.item_estoque import ItemEstoque
from src.estoque.domain.repositories.item_estoque_repository import ItemEstoqueRepository


class EstoqueServiceImpl(EstoqueService):
    """Implementacao in-process para o monolito.
    Este e o UNICO arquivo no catalogo que importa do estoque.
    Nos microsservicos, seria substituido por SNSEstoqueService."""

    def __init__(self, item_estoque_repo: ItemEstoqueRepository) -> None:
        self.item_estoque_repo = item_estoque_repo

    def inicializar_item(self, produto_id: UUID) -> None:
        now = datetime.now(timezone.utc)
        item = ItemEstoque(
            id=uuid4(),
            produto_id=produto_id,
            saldo=0,
            criado_em=now,
            atualizado_em=now,
        )
        self.item_estoque_repo.save(item)
