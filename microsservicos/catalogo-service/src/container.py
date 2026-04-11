import os

from src.application.use_cases.atualizar_produto import AtualizarProdutoUseCase
from src.application.use_cases.buscar_categoria import BuscarCategoriaUseCase
from src.application.use_cases.buscar_produto import BuscarProdutoUseCase
from src.application.use_cases.criar_categoria import CriarCategoriaUseCase
from src.application.use_cases.criar_produto import CriarProdutoUseCase
from src.application.use_cases.desativar_produto import DesativarProdutoUseCase
from src.application.use_cases.listar_categorias import ListarCategoriasUseCase
from src.application.use_cases.listar_produtos import ListarProdutosUseCase


def _build_container():
    is_aws = bool(os.environ.get("CATEGORIAS_TABLE"))

    if is_aws:
        from src.infrastructure.repositories.dynamodb_categoria_repository import DynamoDBCategoriaRepository
        from src.infrastructure.repositories.dynamodb_produto_repository import DynamoDBProdutoRepository
        from src.infrastructure.services.sns_event_publisher import SnsEventPublisher
        cat_repo = DynamoDBCategoriaRepository()
        prod_repo = DynamoDBProdutoRepository()
        event_pub = SnsEventPublisher()
    else:
        from src.infrastructure.repositories.in_memory_categoria_repository import InMemoryCategoriaRepository
        from src.infrastructure.repositories.in_memory_produto_repository import InMemoryProdutoRepository
        from src.infrastructure.services.noop_event_publisher import NoopEventPublisher
        cat_repo = InMemoryCategoriaRepository()
        prod_repo = InMemoryProdutoRepository()
        event_pub = NoopEventPublisher()

    return {
        "criar_categoria": CriarCategoriaUseCase(repo=cat_repo),
        "listar_categorias": ListarCategoriasUseCase(repo=cat_repo),
        "buscar_categoria": BuscarCategoriaUseCase(repo=cat_repo),
        "criar_produto": CriarProdutoUseCase(repo=prod_repo, categoria_repo=cat_repo, event_publisher=event_pub),
        "listar_produtos": ListarProdutosUseCase(repo=prod_repo),
        "buscar_produto": BuscarProdutoUseCase(repo=prod_repo),
        "atualizar_produto": AtualizarProdutoUseCase(repo=prod_repo),
        "desativar_produto": DesativarProdutoUseCase(repo=prod_repo),
    }


container = _build_container()
