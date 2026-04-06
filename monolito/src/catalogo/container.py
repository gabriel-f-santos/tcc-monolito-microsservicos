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


class CatalogoContainer(containers.DeclarativeContainer):
    """Composition Root do BC Catalogo.
    ZERO imports de outros BCs — estoque_service e injetado externamente via app.py."""

    wiring_config = containers.WiringConfiguration(
        modules=["src.catalogo.presentation.routes"],
    )

    # External dependencies
    session_factory = providers.Dependency()
    estoque_service = providers.Dependency()  # Injected by app.py from EstoqueContainer

    # Repositories — own BC only
    categoria_repository = providers.Singleton(
        SQLAlchemyCategoriaRepository,
        session_factory=session_factory,
    )

    produto_repository = providers.Singleton(
        SQLAlchemyProdutoRepository,
        session_factory=session_factory,
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
