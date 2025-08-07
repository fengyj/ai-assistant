"""
OAuth authentication API endpoints.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from ..models.api.oauth_api import OAuthCleanupResponseData, OAuthProvidersResponseData
from ..repositories.json_user_repository import JsonUserRepository
from ..services.oauth_service import OAuthServiceManager, oauth_manager
from ..services.user_service import UserService
from ..utils.auth import CurrentUser, get_current_user
from ..utils.permissions import require_admin


# Dependency injection
def get_user_service() -> UserService:
    """Get user service instance."""
    user_repository = JsonUserRepository()
    return UserService(user_repository)


def get_oauth_manager() -> OAuthServiceManager:
    """Get OAuth service manager."""
    return oauth_manager


# Router
router = APIRouter(prefix="/api/oauth", tags=["oauth"])


@router.get("/providers", response_model=OAuthProvidersResponseData)
async def get_oauth_providers(
    oauth_service: OAuthServiceManager = Depends(get_oauth_manager),
) -> OAuthProvidersResponseData:
    """Get available OAuth providers."""
    available_providers = oauth_service.get_available_providers()

    # All possible providers
    all_providers = ["google", "microsoft", "apple"]
    configured_providers = {provider: provider in available_providers for provider in all_providers}

    return OAuthProvidersResponseData(providers=available_providers, configured_providers=configured_providers)


@router.post("/cleanup", status_code=status.HTTP_200_OK)
@require_admin
async def cleanup_oauth_states(
    oauth_service: OAuthServiceManager = Depends(get_oauth_manager),
    current_user: CurrentUser = Depends(get_current_user),
) -> OAuthCleanupResponseData:
    """Clean up expired OAuth states."""
    try:
        count = await oauth_service.cleanup_expired_states()
        return OAuthCleanupResponseData(message=f"Cleaned up {count} expired OAuth states")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup failed: {str(e)}",
        )


def _generate_username_from_email(email: str) -> str:
    """Generate a unique username from email address."""
    username_base = email.split("@")[0]
    # Remove special characters and make lowercase
    username_base = "".join(c for c in username_base if c.isalnum()).lower()

    # Add a timestamp to ensure uniqueness
    timestamp = str(int(datetime.now().timestamp()))[-6:]
    return f"{username_base}_{timestamp}"
