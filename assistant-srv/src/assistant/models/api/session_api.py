"""
API request and response models for session management.
Separated from core domain models following separation of concerns.
"""

from typing import Optional
from pydantic import BaseModel


class SessionCreateRequestData(BaseModel):
    """Session creation API request data."""
    user_id: str
    device_info: Optional[str] = None
    extend_hours: int = 24


class SessionRefreshRequestData(BaseModel):
    """Session refresh API request data."""
    extend_hours: int = 24
