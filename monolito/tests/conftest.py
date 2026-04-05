from fastapi.testclient import TestClient
import pytest

from src.presentation.app import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
