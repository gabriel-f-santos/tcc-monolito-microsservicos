import boto3
import pytest

from src.container import AuthContainer


@pytest.fixture(autouse=True)
def _dynamo_table():
    """Create an in-memory DynamoDB table for tests using moto isn't needed;
    we use a local DynamoDB-like dict-based fake via container override."""
    pass


@pytest.fixture
def container():
    """Provide an AuthContainer wired with a fake in-memory repository."""
    from tests.fakes import FakeUsuarioRepository

    c = AuthContainer(
        table_name="test-usuarios",
        jwt_secret="test-secret",
        jwt_expiration_hours=24,
    )
    c.usuario_repository.override(FakeUsuarioRepository())
    return c
