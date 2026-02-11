import pytest
from fastapi.testclient import TestClient

from app.api.deps.url_service_dependency import (
    provide_database_name,
    provide_repository,
    provide_url_service,
)
from app.api.views import app
from app.data.repository.repository import Repository
from app.services.url_service import URLService


@pytest.fixture
def mock_repository():
    repo = Repository(":memory:")
    repo.initialize_database()
    return repo


@pytest.fixture
def mock_url_service(mock_repository: Repository):
    return URLService(mock_repository)


@pytest.fixture
def test_api_client(mock_repository: Repository, mock_url_service: URLService):
    app.dependency_overrides[provide_database_name] = lambda: ":memory:"
    app.dependency_overrides[provide_repository] = lambda: mock_repository
    app.dependency_overrides[provide_url_service] = lambda: mock_url_service

    yield TestClient(app)

    app.dependency_overrides.clear()
