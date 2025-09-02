"""
Core module initialization.
"""

from .config import Config
from .env import Env
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

Env.init()
config = Config.from_env()

__all__ = [
    "config",
    "AssistantError",
    "Env",
    "UserError",
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "InvalidCredentialsError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
]
