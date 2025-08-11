"""
Centralized dependency injection for FastAPI.
This module provides all dependency injection functions to avoid code duplication.
"""

from functools import lru_cache
from typing import Generator

from ..repositories.json_model_repository import JsonModelRepository
from ..repositories.json_session_repository import JsonSessionRepository
from ..repositories.json_user_repository import JsonUserRepository
from ..services.model_service import ModelService
from ..services.session_service import SessionService
from ..services.user_service import UserService


# Repository Dependencies (cached)
@lru_cache()
def get_user_repository() -> JsonUserRepository:
    """Get user repository instance (cached)."""
    return JsonUserRepository()


@lru_cache()
def get_session_repository() -> JsonSessionRepository:
    """Get session repository instance (cached)."""
    return JsonSessionRepository()


@lru_cache()
def get_model_repository() -> JsonModelRepository:
    """Get model repository instance (cached)."""
    return JsonModelRepository()


# Service Dependencies
def get_session_service() -> SessionService:
    """Get session service instance."""
    session_repository = get_session_repository()
    return SessionService(session_repository)


def get_user_service() -> UserService:
    """Get user service instance."""
    user_repository = get_user_repository()
    session_repository = get_session_repository()
    return UserService(user_repository, session_repository)


def get_model_service() -> ModelService:
    """Get model service instance."""
    model_repository = get_model_repository()
    return ModelService(model_repository)


# Alternative dependency providers using generators for proper cleanup
def get_user_service_with_cleanup() -> Generator[UserService, None, None]:
    """Get user service instance with proper cleanup."""
    user_repository = get_user_repository()
    session_repository = get_session_repository()
    service = UserService(user_repository, session_repository)
    try:
        yield service
    finally:
        # Add cleanup logic here if needed
        pass


def get_session_service_with_cleanup() -> Generator[SessionService, None, None]:
    """Get session service instance with proper cleanup."""
    session_repository = get_session_repository()
    service = SessionService(session_repository)
    try:
        yield service
    finally:
        # Add cleanup logic here if needed
        pass


def get_model_service_with_cleanup() -> Generator[ModelService, None, None]:
    """Get model service instance with proper cleanup."""
    model_repository = get_model_repository()
    service = ModelService(model_repository)
    try:
        yield service
    finally:
        # Add cleanup logic here if needed
        pass
