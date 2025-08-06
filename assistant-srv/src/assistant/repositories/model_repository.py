"""
Model repository interface.
"""

from abc import abstractmethod
from typing import Optional, List
from .base import BaseRepository
from ..models.model import Model


class ModelRepository(BaseRepository[Model]):
    """Model repository interface."""

    @abstractmethod
    async def list_models_by_owner(self, user_id: str) -> List[Model]:
        """List all models available to the user (system + user)."""
        pass

    @abstractmethod
    async def model_name_exists(
        self, owner: str, name: str, exclude_id: Optional[str] = None
    ) -> bool:
        """Check if a model name exists for an owner."""
        pass

    @abstractmethod
    async def get_user_api_key(
        self, user_id: str, model_id: str
    ) -> Optional[str]:
        """Get API key for a specific user and model."""
        pass

    @abstractmethod
    async def set_user_api_key(
        self, user_id: str, model_id: str, api_key: str
    ) -> None:
        """Set API key for a specific user and model."""
        pass

    @abstractmethod
    async def remove_user_api_key(
        self, user_id: str, model_id: str
    ) -> None:
        """Remove API key for a specific user and model."""
        pass
