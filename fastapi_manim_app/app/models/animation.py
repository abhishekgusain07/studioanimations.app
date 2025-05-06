"""
Models for animation-related data structures.
"""
from enum import Enum


class QualityOption(str, Enum):
    """Animation quality options."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high" 