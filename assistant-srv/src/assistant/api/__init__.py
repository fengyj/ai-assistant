"""
API module initialization.
"""

from .users import router as users_router

__all__ = [
    "users_router",
]
