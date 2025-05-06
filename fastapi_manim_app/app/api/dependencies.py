"""
FastAPI dependency injection functions.
"""
import datetime
from typing import Callable, Generator


def get_current_timestamp() -> str:
    """
    Dependency that provides the current timestamp in ISO format.
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.datetime.now(datetime.timezone.utc).isoformat()