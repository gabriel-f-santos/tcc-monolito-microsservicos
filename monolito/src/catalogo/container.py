from dependency_injector import containers, providers

from src.catalogo.application.use_cases.atualizar_produto import AtualizarProdutoUseCase
from src.catalogo.application.use_cases.buscar_categoria import BuscarCategoriaUseCase
from src.catalogo.application.use_cases.buscar_produto import BuscarProdutoUseCase
from src.catalogo.application.use_cases.criar_categoria import CriarCategoriaUseCase
from src.catalogo.application.use_cases.criar_produto import CriarProdutoUseCase
from src.catalogo.application.use_cases.desativar_produto import DesativarProdutoUseCase
from src.catalogo.application.use_cases.listar_categorias import ListarCategoriasUseCase
from src.catalogo.application.use_cases.listar_produtos import ListarProdutosUseCase
from src.catalogo.infrastructure.repositories.sqlalchemy_categoria_repository import (
    SQLAlchemyCategoriaRepository,
)
from src.catalogo.infrastructure.repositories.sqlalchemy_produto_repository import (
    SQLAlchemyProdutoRepository,
)
from src.catalogo.infrastructure.services.estoque_service_impl import EstoqueServiceImpl
from src.estoque.infrastructure.repositories.sqlalchemy_item_estoque_repository import (
    SQLAlchemyItemEstoqueRepository,
)


class CatalogoContainer(containers.DeclarativeContainer):
    """Composition Root do BC Catalogo.
    Unico lugar que conhece implementacoes concretas.
    O import de estoque.infrastructure aqui e intencional:
    o container e infraestrutura, nao dominio."""

    wiring_config = containers.WiringConfiguration(
        modules=["src.catalogo.presentation.routes"],
    )

    # External dependencies
    session_factory = providers.Dependency()

    # Repositories — own BC
    categoria_repository = providers.Singleton(
        SQLAlchemyCategoriaRepository,
        session_factory=session_factory,
    )

    produto_repository = providers.Singleton(
        SQLAlchemyProdutoRepository,
        session_factory=session_factory,
    )

    # Cross-BC service — interface in domain, implementation in infrastructure
    _item_estoque_repository = providers.Singleton(
        SQLAlchemyItemEstoqueRepository,
        session_factory=session_factory,
    )

    estoque_service = providers.Singleton(
        EstoqueServiceImpl,
        item_estoque_repo=_item_estoque_repository,
    )

    # Use Cases — Categoria
    criar_categoria = providers.Factory(
        CriarCategoriaUseCase,
        repo=categoria_repository,
    )

    listar_categorias = providers.Factory(
        ListarCategoriasUseCase,
        repo=categoria_repository,
    )

    buscar_categoria = providers.Factory(
        BuscarCategoriaUseCase,
        repo=categoria_repository,
    )

    # Use Cases — Produto
    criar_produto = providers.Factory(
        CriarProdutoUseCase,
        repo=produto_repository,
        categoria_repo=categoria_repository,
        estoque_service=estoque_service,
    )

    listar_produtos = providers.Factory(
        ListarProdutosUseCase,
        repo=produto_repository,
    )

    buscar_produto = providers.Factory(
        BuscarProdutoUseCase,
        repo=produto_repository,
    )

    atualizar_produto = providers.Factory(
        AtualizarProdutoUseCase,
        repo=produto_repository,
    )

    desativar_produto = providers.Factory(
        DesativarProdutoUseCase,
        repo=produto_repository,
    )
