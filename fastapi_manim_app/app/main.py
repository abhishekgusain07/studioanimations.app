"""
Main FastAPI application factory.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import animation, health, conversation, message
from app.core.config import settings
from app.core.logging import configure_logging


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging()
    
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        openapi_url=settings.OPENAPI_URL,
    )

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    application.include_router(health.router)
    application.include_router(animation.router)
    application.include_router(conversation.router)
    application.include_router(message.router)
    
    # Mount static directory for serving generated videos
    application.mount(
        settings.SERVED_VIDEOS_PATH_PREFIX,
        StaticFiles(directory=str(settings.STATIC_VIDEOS_DIR)),
        name="manim_videos",
    )

    return application


app = create_application()