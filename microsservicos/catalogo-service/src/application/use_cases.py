from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.application.dtos import (
    AtualizarProdutoDTO,
    CriarCategoriaDTO,
    CriarProdutoDTO,
)
from src.domain.entities import Categoria, Produto
from src.domain.exceptions import (
    CategoriaNaoEncontrada,
    CategoriaNomeDuplicado,
    ProdutoNaoEncontrado,
    ProdutoSkuDuplicado,
)
from src.domain.repositories import CategoriaRepository, ProdutoRepository
from src.domain.services import EventPublisher
from src.domain.value_objects import Dinheiro, SKU


# === Categorias ===


class CriarCategoriaUseCase:
    def __init__(self, repo: CategoriaRepository) -> None:
        self.repo = repo

    def execute(self, dados: CriarCategoriaDTO) -> Categoria:
        if self.repo.get_by_nome(dados.nome) is not None:
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


class ListarCategoriasUseCase:
    def __init__(self, repo: CategoriaRepository) -> None:
        self.repo = repo

    def execute(self) -> list[Categoria]:
        return self.repo.list_all()


class BuscarCategoriaUseCase:
    def __init__(self, repo: CategoriaRepository) -> None:
        self.repo = repo

    def execute(self, categoria_id: UUID) -> Categoria:
        categoria = self.repo.get_by_id(categoria_id)
        if categoria is None:
            raise CategoriaNaoEncontrada()
        return categoria


# === Produtos ===


class CriarProdutoUseCase:
    def __init__(
        self,
        repo: ProdutoRepository,
        categoria_repo: CategoriaRepository,
        event_publisher: EventPublisher,
    ) -> None:
        self.repo = repo
        self.categoria_repo = categoria_repo
        self.event_publisher = event_publisher

    def execute(self, dados: CriarProdutoDTO) -> Produto:
        categoria = self.categoria_repo.get_by_id(dados.categoria_id)
        if categoria is None:
            raise CategoriaNaoEncontrada()

        sku_vo = SKU(valor=dados.sku)
        if self.repo.get_by_sku(sku_vo.valor) is not None:
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

        self.event_publisher.publicar_produto_criado(
            produto_id=produto.id,
            sku=produto.sku.valor,
            nome=produto.nome,
            categoria_nome=categoria.nome,
        )
        return produto


class ListarProdutosUseCase:
    def __init__(self, repo: ProdutoRepository) -> None:
        self.repo = repo

    def execute(
        self,
        categoria_id: UUID | None = None,
        ativo: bool | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Produto]:
        return self.repo.list_filtered(
            categoria_id=categoria_id, ativo=ativo, page=page, size=size
        )


class BuscarProdutoUseCase:
    def __init__(self, repo: ProdutoRepository) -> None:
        self.repo = repo

    def execute(self, produto_id: UUID) -> Produto:
        produto = self.repo.get_by_id(produto_id)
        if produto is None:
            raise ProdutoNaoEncontrado()
        return produto


class AtualizarProdutoUseCase:
    def __init__(self, repo: ProdutoRepository) -> None:
        self.repo = repo

    def execute(self, produto_id: UUID, dados: AtualizarProdutoDTO) -> Produto:
        produto = self.repo.get_by_id(produto_id)
        if produto is None:
            raise ProdutoNaoEncontrado()
        produto.atualizar(
            nome=dados.nome, descricao=dados.descricao, preco=dados.preco
        )
        return self.repo.save(produto)


class DesativarProdutoUseCase:
    def __init__(self, repo: ProdutoRepository) -> None:
        self.repo = repo

    def execute(self, produto_id: UUID) -> Produto:
        produto = self.repo.get_by_id(produto_id)
        if produto is None:
            raise ProdutoNaoEncontrado()
        produto.desativar()
        return self.repo.save(produto)
