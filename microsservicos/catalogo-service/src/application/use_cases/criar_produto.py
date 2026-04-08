from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.entities.produto import Produto
from src.domain.exceptions.catalogo import CategoriaNaoEncontrada, ProdutoSkuDuplicado
from src.domain.repositories.categoria_repository import CategoriaRepository
from src.domain.repositories.produto_repository import ProdutoRepository
from src.shared.domain.services.estoque_service import EstoqueService
from src.domain.value_objects.dinheiro import Dinheiro
from src.domain.value_objects.sku import SKU


@dataclass
class CriarProdutoDTO:
    sku: str
    nome: str
    preco: Decimal
    categoria_id: UUID
    descricao: str | None = None


class CriarProdutoUseCase:
    def __init__(
        self,
        repo: ProdutoRepository,
        categoria_repo: CategoriaRepository,
        estoque_service: EstoqueService,
    ) -> None:
        self.repo = repo
        self.categoria_repo = categoria_repo
        self.estoque_service = estoque_service

    def execute(self, dados: CriarProdutoDTO) -> Produto:
        # Uniqueness check — acceptable at application layer
        categoria = self.categoria_repo.get_by_id(dados.categoria_id)
        if categoria is None:
            raise CategoriaNaoEncontrada()

        sku_vo = SKU(valor=dados.sku)
        existente = self.repo.get_by_sku(sku_vo.valor)
        if existente is not None:
            raise ProdutoSkuDuplicado()

        now = datetime.now(timezone.utc)
        produto = Produto(
            id=uuid4(),
            sku=sku_vo,
            nome=dados.nome,
            descricao=dados.descricao,
            preco=Dinheiro(valor=dados.preco),
            categoria_id=dados.categoria_id,
            ativo=True,
            criado_em=now,
            atualizado_em=now,
        )
        produto = self.repo.save(produto)

        # Comunicacao cross-BC via interface (nao import direto)
        self.estoque_service.inicializar_item(
            produto_id=produto.id,
            sku=produto.sku.valor,
            nome_produto=produto.nome,
            categoria_nome=categoria.nome,
        )

        return produto
