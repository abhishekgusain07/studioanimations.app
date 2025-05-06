"""
PyTest configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import create_application


@pytest.fixture
def app():
    """Create a fresh app instance for testing."""
    return create_application()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return TestClient(app)