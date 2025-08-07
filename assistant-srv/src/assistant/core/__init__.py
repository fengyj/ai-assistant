"""
Core module initialization.
"""

from .config import config
from .exceptions import (
    AssistantError,
    AuthenticationError,
    AuthorizationError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserError,
    UserNotFoundError,
    ValidationError,
)

__all__ = [
    "config",
    "AssistantError",
    "UserError",
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "InvalidCredentialsError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
]
