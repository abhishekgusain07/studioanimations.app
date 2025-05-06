"""
Tests for the health check endpoint.
"""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


def test_health_check(client: TestClient):
    """Test that the health check endpoint returns 200 and expected data."""
    # Given a running application
    
    # When a request is made to the health endpoint
    response = client.get("/health")
    
    # Then the response should be successful
    assert response.status_code == 200
    
    # And the response should contain expected health information
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == settings.VERSION
    assert data["environment"] == settings.ENVIRONMENT


@patch("app.api.dependencies.get_current_timestamp")
def test_health_check_with_fixed_timestamp(mock_timestamp, client: TestClient):
    """Test health check with a mocked timestamp."""
    # Given a fixed timestamp
    mock_timestamp.return_value = "2025-05-06T12:00:00+00:00"
    
    # When a request is made to the health endpoint
    response = client.get("/health")
    
    # Then the response should be successful
    assert response.status_code == 200
    
    # And the response should contain the mocked timestamp
    data = response.json()
    assert data["timestamp"] == "2025-05-06T12:00:00+00:00"