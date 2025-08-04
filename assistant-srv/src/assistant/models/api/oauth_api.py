"""
API request and response models for OAuth authentication.
Separated from core domain models following separation of concerns.
"""

from typing import Optional, Dict
from pydantic import BaseModel, EmailStr


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request."""

    code: str
    state: str
    error: Optional[str] = None
    error_description: Optional[str] = None


class OAuthUserInfo(BaseModel):
    """OAuth user information."""

    provider_id: str
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class OAuthLoginResponse(BaseModel):
    """OAuth login response."""

    user_id: str
    username: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    status: str
    is_new_user: bool
    access_token: Optional[str] = None  # For future JWT implementation


class OAuthProvidersResponse(BaseModel):
    """Available OAuth providers response."""

    providers: list[str]
    configured_providers: Dict[str, bool]


class OAuthAuthorizeResponse(BaseModel):
    """OAuth authorization response."""

    authorize_url: str
    state: str
    provider: str
    expires_in: int = 600  # 10 minutes
