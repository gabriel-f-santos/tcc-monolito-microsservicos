from dependency_injector import containers, providers

from src.catalogo.application.use_cases.buscar_categoria import BuscarCategoriaUseCase
from src.catalogo.application.use_cases.criar_categoria import CriarCategoriaUseCase
from src.catalogo.application.use_cases.listar_categorias import ListarCategoriasUseCase
from src.catalogo.infrastructure.repositories.sqlalchemy_categoria_repository import (
    SQLAlchemyCategoriaRepository,
)


class CatalogoContainer(containers.DeclarativeContainer):
    """Composition Root do BC Catalogo."""

    wiring_config = containers.WiringConfiguration(
        modules=["src.catalogo.presentation.routes"],
    )

    # External dependencies
    session_factory = providers.Dependency()

    # Repository
    categoria_repository = providers.Singleton(
        SQLAlchemyCategoriaRepository,
        session_factory=session_factory,
    )

    # Use Cases
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
