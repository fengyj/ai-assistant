"""
API models module exports.
Centralizes all API model imports for easier access.
"""

from .auth_api import (
    LoginRequestData,
    LoginResponseData,
    LogoutResponseData,
    RefreshTokenRequestData,
    RefreshTokenResponseData,
)

# Model API models
from .model_api import ModelRequestData, ModelResponseData
from .oauth_api import (
    OAuthAuthorizeResponseData,
    OAuthCallbackRequestData,
    OAuthCleanupResponseData,
    OAuthLoginRequestData,
    OAuthLoginResponseData,
    OAuthProvidersResponseData,
    OAuthUserInfoData,
)

# Session API models
from .session_api import SessionCreateRequestData, SessionRefreshRequestData

# User API models
from .user_api import (
    EmailChangeRequestData,
    PasswordChangeRequestData,
    RoleChangeRequestData,
    UserCreateRequestData,
    UserResponseData,
    UserUpdateRequestData,
)

__all__ = [
    # User API
    "UserCreateRequestData",
    "UserUpdateRequestData",
    "EmailChangeRequestData",
    "RoleChangeRequestData",
    "PasswordChangeRequestData",
    "UserResponseData",
    # OAuth API
    "OAuthCallbackRequestData",
    "OAuthUserInfoData",
    "OAuthLoginResponseData",
    "OAuthProvidersResponseData",
    "OAuthAuthorizeResponseData",
    "OAuthLoginRequestData",
    "OAuthCleanupResponseData",
    # Session API
    "SessionCreateRequestData",
    "SessionRefreshRequestData",
    # Model API
    "ModelRequestData",
    "ModelResponseData",
    # Auth API
    "LoginRequestData",
    "LoginResponseData",
    "RefreshTokenRequestData",
    "RefreshTokenResponseData",
    "LogoutResponseData",
]
