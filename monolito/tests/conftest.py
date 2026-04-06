from fastapi.testclient import TestClient
import pytest

from src.shared.infrastructure.database.base import Base
from src.shared.infrastructure.database.session import engine
from src.presentation.app import app

# Import all models so Base.metadata knows about them
import src.auth.infrastructure.repositories.sqlalchemy_usuario_repository  # noqa: F401
import src.catalogo.infrastructure.repositories.sqlalchemy_categoria_repository  # noqa: F401
import src.catalogo.infrastructure.repositories.sqlalchemy_produto_repository  # noqa: F401
import src.estoque.infrastructure.repositories.sqlalchemy_item_estoque_repository  # noqa: F401
import src.estoque.infrastructure.repositories.sqlalchemy_movimentacao_repository  # noqa: F401


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
