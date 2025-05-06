"""
Application configuration settings loaded from environment variables.
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import AnyHttpUrl, field_validator, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application metadata
    PROJECT_NAME: str = "FastAPI Manim App"
    PROJECT_DESCRIPTION: str = "A FastAPI application for generating Manim animations"
    VERSION: str = "0.1.0"
    
    # API Documentation
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Environment settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Log settings
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = False
    
    # Manim settings
    TEMP_BASE_DIR: Path = Path("temp_manim_jobs")
    STATIC_VIDEOS_DIR: Path = Path("temp_manim_jobs/public_videos")
    SERVED_VIDEOS_PATH_PREFIX: str = "/manim_videos"

    # Database settings
    DATABASE_URL: Optional[str] = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "manim_app"
    DATABASE_ECHO: bool = False
    
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Assemble database connection string from components or use DATABASE_URL if provided."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Test database - used for pytest
    TEST_POSTGRES_DB: str = "test_manim_app"
    
    @computed_field
    @property
    def TEST_SQLALCHEMY_DATABASE_URI(self) -> str:
        """Assemble test database connection string."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.TEST_POSTGRES_DB}"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        """Parse CORS origins from comma-separated string or use default list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create a global settings instance
settings = Settings()

# Ensure required directories exist
os.makedirs(settings.TEMP_BASE_DIR, exist_ok=True)
os.makedirs(settings.STATIC_VIDEOS_DIR, exist_ok=True)