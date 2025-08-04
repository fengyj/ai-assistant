"""
User repository interface.
"""

from abc import abstractmethod
from typing import Optional, List
from .base import BaseRepository
from ..models import User


class UserRepository(BaseRepository[User]):
    """User repository interface."""

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    async def get_by_oauth(self, provider: str, provider_id: str) -> Optional[User]:
        """Get user by OAuth provider and ID."""
        pass

    @abstractmethod
    async def search_users(self, query: str, limit: int = 10) -> List[User]:
        """Search users by query."""
        pass

    @abstractmethod
    async def get_active_users(self) -> List[User]:
        """Get all active users."""
        pass
