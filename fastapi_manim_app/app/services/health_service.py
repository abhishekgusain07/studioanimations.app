"""
Health service functionality.
"""
import platform
from typing import Dict, Any

import structlog
from fastapi import Depends

from app.core.config import settings

# Create a logger for this module
logger = structlog.get_logger(__name__)


class HealthService:
    """Service for handling health-related operations."""
    
    def get_health_info(self, timestamp: str) -> Dict[str, Any]:
        """
        Get health information about the application.
        
        Args:
            timestamp: Current timestamp
            
        Returns:
            Dictionary with health status information
        """
        logger.debug("Retrieving health information")
        
        return {
            "status": "healthy",
            "timestamp": timestamp,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "python_version": platform.python_version(),
        }


def get_health_service() -> HealthService:
    """
    Dependency to get a HealthService instance.
    
    Returns:
        HealthService instance
    """
    return HealthService()