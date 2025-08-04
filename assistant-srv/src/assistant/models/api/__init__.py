"""
API models module exports.
Centralizes all API model imports for easier access.
"""

# User API models
from .user_api import (
    UserCreateAPI,
    UserUpdateAPI,
    EmailChangeAPI,
    RoleChangeAPI,
    LoginAPI,
    PasswordChangeAPI,
    OAuthLoginAPI,
    UserResponseAPI,
    TokenResponse,
)

# OAuth API models
from .oauth_api import (
    OAuthCallbackRequest,
    OAuthUserInfo,
    OAuthLoginResponse,
    OAuthProvidersResponse,
    OAuthAuthorizeResponse,
)

# Session API models
from .session_api import SessionCreateAPI, SessionRefreshAPI

__all__ = [
    # User API
    "UserCreateAPI",
    "UserUpdateAPI",
    "EmailChangeAPI",
    "RoleChangeAPI",
    "LoginAPI",
    "PasswordChangeAPI",
    "OAuthLoginAPI",
    "UserResponseAPI",
    "TokenResponse",
    # OAuth API
    "OAuthCallbackRequest",
    "OAuthUserInfo",
    "OAuthLoginResponse",
    "OAuthProvidersResponse",
    "OAuthAuthorizeResponse",
    # Session API
    "SessionCreateAPI",
    "SessionRefreshAPI",
]
