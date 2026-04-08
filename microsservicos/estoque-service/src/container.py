from dependency_injector import containers, providers

from src.application.use_cases.atualizar_projecao import AtualizarProjecaoUseCase
from src.application.use_cases.buscar_item import BuscarItemUseCase
from src.application.use_cases.criar_item_estoque import CriarItemEstoqueUseCase
from src.application.use_cases.listar_itens import ListarItensUseCase
from src.application.use_cases.listar_movimentacoes import ListarMovimentacoesUseCase
from src.application.use_cases.registrar_entrada import RegistrarEntradaUseCase
from src.application.use_cases.registrar_saida import RegistrarSaidaUseCase
from src.infrastructure.repositories.dynamodb_item_estoque_repository import (
    DynamoDBItemEstoqueRepository,
)
from src.infrastructure.repositories.dynamodb_movimentacao_repository import (
    DynamoDBMovimentacaoRepository,
)


class EstoqueContainer(containers.DeclarativeContainer):
    """Composition Root do BC Estoque (microsservico)."""

    wiring_config = containers.WiringConfiguration(
        modules=["src.presentation.handlers.estoque"],
    )

    # External dependencies
    itens_estoque_table = providers.Dependency(instance_of=str)
    movimentacoes_table = providers.Dependency(instance_of=str)
    endpoint_url = providers.Dependency(default=None)

    # Repositories
    item_estoque_repository = providers.Singleton(
        DynamoDBItemEstoqueRepository,
        table_name=itens_estoque_table,
        endpoint_url=endpoint_url,
    )

    movimentacao_repository = providers.Singleton(
        DynamoDBMovimentacaoRepository,
        table_name=movimentacoes_table,
        endpoint_url=endpoint_url,
    )

    # Use Cases — copied from monolith
    registrar_entrada = providers.Factory(
        RegistrarEntradaUseCase,
        item_repo=item_estoque_repository,
        mov_repo=movimentacao_repository,
    )

    registrar_saida = providers.Factory(
        RegistrarSaidaUseCase,
        item_repo=item_estoque_repository,
        mov_repo=movimentacao_repository,
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

    # Use Cases — new (event-driven)
    criar_item_estoque = providers.Factory(
        CriarItemEstoqueUseCase,
        repo=item_estoque_repository,
    )

    atualizar_projecao = providers.Factory(
        AtualizarProjecaoUseCase,
        repo=item_estoque_repository,
    )
