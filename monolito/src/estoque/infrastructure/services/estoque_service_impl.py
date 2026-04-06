from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.shared.domain.services.estoque_service import EstoqueService
from src.estoque.domain.entities.item_estoque import ItemEstoque
from src.estoque.domain.repositories.item_estoque_repository import ItemEstoqueRepository


class EstoqueServiceImpl(EstoqueService):
    """Implementacao in-process para o monolito.
    Vive no BC de Estoque pois cria entidades do Estoque.
    O Catalogo conhece apenas a interface (EstoqueService).
    app.py wires esta implementacao no CatalogoContainer."""

    def __init__(self, item_estoque_repo: ItemEstoqueRepository) -> None:
        self.item_estoque_repo = item_estoque_repo

    def inicializar_item(
        self,
        produto_id: UUID,
        sku: str,
        nome_produto: str,
        categoria_nome: str,
    ) -> None:
        now = datetime.now(timezone.utc)
        item = ItemEstoque(
            id=uuid4(),
            produto_id=produto_id,
            sku=sku,
            nome_produto=nome_produto,
            categoria_nome=categoria_nome,
            saldo=0,
            ativo=True,
            criado_em=now,
            atualizado_em=now,
        )
        self.item_estoque_repo.save(item)
