from fastapi.testclient import TestClient
import pytest

from src.auth.infrastructure.repositories.sqlalchemy_usuario_repository import Base
from src.shared.infrastructure.database.session import engine
from src.presentation.app import app


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
