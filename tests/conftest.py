import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app


@pytest.fixture
def client():
    store.reset()
    with TestClient(app) as test_client:
        yield test_client
