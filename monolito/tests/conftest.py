from fastapi.testclient import TestClient
import pytest

from src.auth.infrastructure.repositories.sqlalchemy_usuario_repository import Base as AuthBase
from src.catalogo.infrastructure.repositories.sqlalchemy_categoria_repository import Base as CatalogoBase
from src.shared.infrastructure.database.session import engine
from src.presentation.app import app


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    AuthBase.metadata.create_all(engine)
    CatalogoBase.metadata.create_all(engine)
    yield
    CatalogoBase.metadata.drop_all(engine)
    AuthBase.metadata.drop_all(engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
