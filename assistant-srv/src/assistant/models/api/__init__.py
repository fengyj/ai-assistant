"""
API models module exports.
Centralizes all API model imports for easier access.
"""

# Model API models
from .model_api import ModelRequestData, ModelResponseData

# OAuth API models
from .oauth_api import (
    OAuthAuthorizeResponseData,
    OAuthCallbackRequestData,
    OAuthLoginResponseData,
    OAuthProvidersResponseData,
    OAuthUserInfoData,
)

# Session API models
from .session_api import SessionCreateRequestData, SessionRefreshRequestData

# User API models
from .user_api import (
    EmailChangeRequestData,
    LoginRequestData,
    OAuthLoginRequestData,
    PasswordChangeRequestData,
    RoleChangeRequestData,
    TokenResponseData,
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
    "LoginRequestData",
    "PasswordChangeRequestData",
    "OAuthLoginRequestData",
    "UserResponseData",
    "TokenResponseData",
    # OAuth API
    "OAuthCallbackRequestData",
    "OAuthUserInfoData",
    "OAuthLoginResponseData",
    "OAuthProvidersResponseData",
    "OAuthAuthorizeResponseData",
    # Session API
    "SessionCreateRequestData",
    "SessionRefreshRequestData",
    # Model API
    "ModelRequestData",
    "ModelResponseData",
]
