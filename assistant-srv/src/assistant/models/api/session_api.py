"""
API request and response models for session management.
Separated from core domain models following separation of concerns.
"""

from typing import Optional
from pydantic import BaseModel


class SessionCreateAPI(BaseModel):
    """Session creation API model."""

    user_id: str
    device_info: Optional[str] = None
    extend_hours: int = 24


class SessionRefreshAPI(BaseModel):
    """Session refresh API model."""

    extend_hours: int = 24
