"""
API request and response models for OAuth authentication.
Separated from core domain models following separation of concerns.
"""

from typing import Optional, Dict, List
from pydantic import BaseModel, EmailStr


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
    user_id: str
    username: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    status: str
    is_new_user: bool
    access_token: Optional[str] = None  # For future JWT implementation


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
