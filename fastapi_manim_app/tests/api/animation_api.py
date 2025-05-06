"""
Tests for the animation generation API.
"""
import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.services.manim_service import generate_animation_from_query


@pytest.fixture
def app() -> FastAPI:
    """Create a FastAPI app for testing."""
    from app.main import app
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.mark.asyncio
@patch("app.api.routes.animation.generate_animation_from_query")
async def test_generate_animation_success(
    mock_generate: AsyncMock,
    app: FastAPI,
) -> None:
    """Test successful animation generation."""
    # Setup mock
    mock_generate.return_value = (True, "/manim_videos/test_video.mp4", "")
    
    # Make request
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/generate-animation",
            json={"query": "animate a triangle morphing into a square"}
        )
    
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "video_url": "/manim_videos/test_video.mp4",
        "message": "Animation generated successfully"
    }
    
    # Verify mock was called correctly
    mock_generate.assert_called_once_with("animate a triangle morphing into a square")


@pytest.mark.asyncio
@patch("app.api.routes.animation.generate_animation_from_query")
async def test_generate_animation_failure(
    mock_generate: AsyncMock,
    app: FastAPI,
) -> None:
    """Test animation generation failure."""
    # Setup mock
    mock_generate.return_value = (False, "", "Manim execution failed")
    
    # Make request
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/generate-animation",
            json={"query": "animate a triangle morphing into a square"}
        )
    
    # Check response
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Manim execution failed"
    }
    
    # Verify mock was called correctly
    mock_generate.assert_called_once_with("animate a triangle morphing into a square") 