"""
API request and response models for general application endpoints.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class StatusResponseData(BaseModel):
    """Application status response API model."""

    success: bool = True
    status: str
    data: Optional[Dict[str, Any]] = None


class HealthCheckResponseData(BaseModel):
    """Health check response API model."""

    success: bool = True
    status: str
    timestamp: str
    version: Optional[str] = None
