"""
API models module exports.
Centralizes all API model imports for easier access.
"""

# User API models
from .user_api import (
    UserCreateRequestData,
    UserUpdateRequestData,
    EmailChangeRequestData,
    RoleChangeRequestData,
    LoginRequestData,
    PasswordChangeRequestData,
    OAuthLoginRequestData,
    UserResponseData,
    TokenResponseData,
)

# OAuth API models
from .oauth_api import (
    OAuthCallbackRequestData,
    OAuthUserInfoData,
    OAuthLoginResponseData,
    OAuthProvidersResponseData,
    OAuthAuthorizeResponseData,
)

# Session API models
from .session_api import SessionCreateRequestData, SessionRefreshRequestData

# Model API models
from .model_api import ModelRequestData, ModelResponseData

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
