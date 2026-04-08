from dependency_injector import containers, providers

from src.application.use_cases.atualizar_produto import AtualizarProdutoUseCase
from src.application.use_cases.buscar_categoria import BuscarCategoriaUseCase
from src.application.use_cases.buscar_produto import BuscarProdutoUseCase
from src.application.use_cases.criar_categoria import CriarCategoriaUseCase
from src.application.use_cases.criar_produto import CriarProdutoUseCase
from src.application.use_cases.desativar_produto import DesativarProdutoUseCase
from src.application.use_cases.listar_categorias import ListarCategoriasUseCase
from src.application.use_cases.listar_produtos import ListarProdutosUseCase
from src.infrastructure.repositories.dynamodb_categoria_repository import (
    DynamoDBCategoriaRepository,
)
from src.infrastructure.repositories.dynamodb_produto_repository import (
    DynamoDBProdutoRepository,
)
from src.infrastructure.services.sns_estoque_service import SNSEstoqueService


class CatalogoContainer(containers.DeclarativeContainer):
    """Composition Root do BC Catalogo (microsservico)."""

    wiring_config = containers.WiringConfiguration(
        modules=["src.presentation.handlers.catalogo"],
    )

    # External dependencies
    produtos_table = providers.Dependency(instance_of=str)
    categorias_table = providers.Dependency(instance_of=str)
    endpoint_url = providers.Dependency(default=None)
    eventos_topic_arn = providers.Dependency(instance_of=str)

    # Repositories
    produto_repository = providers.Singleton(
        DynamoDBProdutoRepository,
        table_name=produtos_table,
        endpoint_url=endpoint_url,
    )

    categoria_repository = providers.Singleton(
        DynamoDBCategoriaRepository,
        table_name=categorias_table,
        endpoint_url=endpoint_url,
    )

    # Cross-BC service
    estoque_service = providers.Singleton(
        SNSEstoqueService,
        topic_arn=eventos_topic_arn,
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
