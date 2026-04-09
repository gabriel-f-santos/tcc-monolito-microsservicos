from fastapi.testclient import TestClient
import pytest

from app import app
from database import Base, engine


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# --- Helpers ---

def _register_and_login(client: TestClient) -> str:
    """Registra usuario e retorna token JWT."""
    import uuid
    email = f"test-{uuid.uuid4().hex[:8]}@test.com"
    client.post("/api/v1/auth/registrar", json={
        "nome": "Test User",
        "email": email,
        "senha": "senha12345",
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": email,
        "senha": "senha12345",
    })
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
