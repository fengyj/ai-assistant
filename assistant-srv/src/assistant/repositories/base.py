"""
Abstract base repository interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar("T")


class BaseRepository(Generic[T], ABC):
    """Base repository interface."""

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        """Get all entities."""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an entity."""
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity."""
        pass

    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """Check if entity exists."""
        pass
