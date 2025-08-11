"""
API request and response models for OAuth authentication.
Separated from core domain models following separation of concerns.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr

from .user_api import UserResponseData


class OAuthLoginRequestData(BaseModel):
    """OAuth login API request model."""

    provider: str
    provider_id: str
    email: str
    username: str
    display_name: Optional[str] = None
    avatar: Optional[str] = None


class OAuthCallbackRequestData(BaseModel):
    """OAuth callback request data."""

    code: str
    state: str
    error: Optional[str] = None
    error_description: Optional[str] = None


class OAuthUserInfoData(BaseModel):
    """OAuth user information data."""

    provider_id: str
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class OAuthLoginResponseData(BaseModel):
    """OAuth login response data."""

    access_token: str
    token_type: str
    user: UserResponseData
    is_new_user: bool


class OAuthProvidersResponseData(BaseModel):
    """OAuth providers response data."""

    providers: List[str]
    configured_providers: Dict[str, bool]


class OAuthCleanupResponseData(BaseModel):
    """OAuth cleanup response API model."""

    success: bool = True
    message: str


class OAuthAuthorizeResponseData(BaseModel):
    """OAuth authorization response data."""

    authorize_url: str
    state: str
    provider: str
    expires_in: int = 600  # 10 minutes
