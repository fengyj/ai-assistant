"""
Session repository interface.
"""

from abc import abstractmethod
from typing import List, Optional

from ..models.session import UserSession
from .base import BaseRepository


class SessionRepository(BaseRepository[UserSession]):
    """Session repository interface."""

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[UserSession]:
        """Get session by token."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[UserSession]:
        """Get all sessions for a user."""
        pass

    @abstractmethod
    async def get_active_sessions(self, user_id: str) -> List[UserSession]:
        """Get active sessions for a user."""
        pass

    @abstractmethod
    async def terminate_user_sessions(self, user_id: str) -> int:
        """Terminate all sessions for a user."""
        pass

    @abstractmethod
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        pass
