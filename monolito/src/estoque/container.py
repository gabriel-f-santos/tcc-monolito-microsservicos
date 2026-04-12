from dependency_injector import containers, providers

from src.estoque.application.use_cases.buscar_item import BuscarItemUseCase
from src.estoque.application.use_cases.configurar_alerta import ConfigurarAlertaUseCase
from src.estoque.application.use_cases.listar_alertas import ListarAlertasUseCase
from src.estoque.application.use_cases.listar_itens import ListarItensUseCase
from src.estoque.application.use_cases.listar_movimentacoes import ListarMovimentacoesUseCase
from src.estoque.application.use_cases.registrar_entrada import RegistrarEntradaUseCase
from src.estoque.application.use_cases.registrar_saida import RegistrarSaidaUseCase
from src.estoque.infrastructure.repositories.sqlalchemy_alerta_estoque_repository import (
    SQLAlchemyAlertaEstoqueRepository,
)
from src.estoque.infrastructure.repositories.sqlalchemy_item_estoque_repository import (
    SQLAlchemyItemEstoqueRepository,
)
from src.estoque.infrastructure.repositories.sqlalchemy_movimentacao_repository import (
    SQLAlchemyMovimentacaoRepository,
)


class EstoqueContainer(containers.DeclarativeContainer):
    """Composition Root do BC Estoque."""

    wiring_config = containers.WiringConfiguration(
        modules=["src.estoque.presentation.routes"],
    )

    # External dependencies
    session_factory = providers.Dependency()

    # Repositories
    item_estoque_repository = providers.Singleton(
        SQLAlchemyItemEstoqueRepository,
        session_factory=session_factory,
    )

    movimentacao_repository = providers.Singleton(
        SQLAlchemyMovimentacaoRepository,
        session_factory=session_factory,
    )

    alerta_estoque_repository = providers.Singleton(
        SQLAlchemyAlertaEstoqueRepository,
        session_factory=session_factory,
    )

    # Use Cases
    registrar_entrada = providers.Factory(
        RegistrarEntradaUseCase,
        item_repo=item_estoque_repository,
        mov_repo=movimentacao_repository,
    )

    registrar_saida = providers.Factory(
        RegistrarSaidaUseCase,
        item_repo=item_estoque_repository,
        mov_repo=movimentacao_repository,
        alerta_repo=alerta_estoque_repository,
    )

    configurar_alerta = providers.Factory(
        ConfigurarAlertaUseCase,
        item_repo=item_estoque_repository,
    )

    listar_alertas = providers.Factory(
        ListarAlertasUseCase,
        item_repo=item_estoque_repository,
        alerta_repo=alerta_estoque_repository,
    )

    listar_itens = providers.Factory(
        ListarItensUseCase,
        repo=item_estoque_repository,
    )

    buscar_item = providers.Factory(
        BuscarItemUseCase,
        repo=item_estoque_repository,
    )

    listar_movimentacoes = providers.Factory(
        ListarMovimentacoesUseCase,
        item_repo=item_estoque_repository,
        mov_repo=movimentacao_repository,
    )
