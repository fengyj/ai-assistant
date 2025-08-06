"""
OAuth authentication endpoints.
Focused on HTTP layer concerns only, business logic delegated to services.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status, Request

from ..models import User, UserRole, UserStatus, OAuthProvider, OAuthInfo, UserProfile
from ..models.api.oauth_api import (
    OAuthCallbackRequestData,
    OAuthUserInfoData,
    OAuthLoginResponseData,
    OAuthProvidersResponseData,
    OAuthAuthorizeResponseData,
)
from ..services.user_service import UserService
from ..services.oauth_service import oauth_manager
from ..repositories.json_user_repository import JsonUserRepository
from ..core.exceptions import ValidationError
from ..utils.auth import get_current_active_user, CurrentUser
from ..utils.permissions import require_admin, require_owner_or_admin


# Dependency injection
def get_user_service() -> UserService:
    """Get user service instance."""
    user_repository = JsonUserRepository()
    return UserService(user_repository)


def get_oauth_manager() -> object:
    """Get OAuth service manager."""
    return oauth_manager


# Router
router = APIRouter(prefix="/api/oauth", tags=["oauth"])


@router.get("/providers", response_model=OAuthProvidersResponseData)
async def get_oauth_providers(oauth_service: object = Depends(get_oauth_manager)) -> OAuthProvidersResponseData:
    """Get available OAuth providers."""
    available_providers = oauth_service.get_available_providers()

    # All possible providers
    all_providers = ["google", "microsoft", "apple"]
    configured_providers = {
        provider: provider in available_providers for provider in all_providers
    }

    return OAuthProvidersResponseData(
        providers=available_providers, configured_providers=configured_providers
    )


@router.get("/{provider}/authorize", response_model=OAuthAuthorizeResponseData)
async def get_oauth_authorize_url(
    provider: str, request: Request, oauth_service: object = Depends(get_oauth_manager)
) -> OAuthAuthorizeResponseData:
    """Get OAuth authorization URL for the specified provider."""
    try:
        # Check if provider is available
        if not oauth_service.is_provider_available(provider.lower()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth provider '{provider}' is not configured",
            )

        # Generate authorization URL with metadata
        metadata = {
            "user_agent": request.headers.get("user-agent"),
            "ip_address": request.client.host if request.client else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        auth_url, state_token = oauth_service.generate_authorization_url(
            provider.lower(), metadata
        )

        return OAuthAuthorizeResponseData(
            authorize_url=auth_url, state=state_token, provider=provider.lower()
        )

    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate authorization URL: {str(e)}",
        )


@router.post("/{provider}/callback", response_model=OAuthLoginResponseData)
async def oauth_callback(
    provider: str,
    callback_data: OAuthCallbackRequestData,
    request: Request,
    user_service: UserService = Depends(get_user_service),
    oauth_service: object = Depends(get_oauth_manager),
) -> OAuthLoginResponseData:
    """Handle OAuth callback and login/register user."""
    try:
        # Check for OAuth errors
        if callback_data.error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth error: {callback_data.error} - {callback_data.error_description}",
            )

        # Handle OAuth callback
        user_profile = await oauth_service.handle_callback(
            provider.lower(), callback_data.code, callback_data.state
        )

        # Convert provider name to enum
        oauth_provider = OAuthProvider(provider.lower())

        # Check if user exists by OAuth provider info
        existing_user = await user_service.get_user_by_oauth(
            oauth_provider.value, user_profile.provider_id
        )

        is_new_user = False

        if existing_user:
            # Update existing OAuth user
            existing_user.last_login = datetime.now(timezone.utc)
            existing_user.usage_stats.total_sessions += 1

            # Update profile information if available
            if user_profile.name and not existing_user.profile.display_name:
                existing_user.profile.display_name = user_profile.name
            if user_profile.avatar_url and not existing_user.profile.avatar_url:
                existing_user.profile.avatar_url = user_profile.avatar_url

            user = await user_service.user_repository.update(existing_user)
        else:
            # Check if user exists by email
            existing_user = await user_service.get_user_by_email(user_profile.email)

            if existing_user:
                # Add OAuth info to existing email user
                oauth_info = OAuthInfo(
                    provider=oauth_provider,
                    provider_id=user_profile.provider_id,
                    email=user_profile.email,
                    name=user_profile.name,
                    avatar_url=user_profile.avatar_url,
                )
                existing_user.oauth_info.append(oauth_info)
                existing_user.last_login = datetime.now(timezone.utc)
                existing_user.usage_stats.total_sessions += 1

                # Update profile if empty
                if user_profile.name and not existing_user.profile.display_name:
                    existing_user.profile.display_name = user_profile.name
                if user_profile.avatar_url and not existing_user.profile.avatar_url:
                    existing_user.profile.avatar_url = user_profile.avatar_url

                user = await user_service.user_repository.update(existing_user)
            else:
                # Create new user from OAuth
                is_new_user = True
                user = User(
                    username=_generate_username_from_email(user_profile.email),
                    email=user_profile.email,
                    role=UserRole.USER,
                    status=UserStatus.ACTIVE,
                    profile=UserProfile(
                        display_name=user_profile.name,
                        avatar_url=user_profile.avatar_url,
                        language="en",
                    ),
                    oauth_info=[
                        OAuthInfo(
                            provider=oauth_provider,
                            provider_id=user_profile.provider_id,
                            email=user_profile.email,
                            name=user_profile.name,
                            avatar_url=user_profile.avatar_url,
                        )
                    ],
                    last_login=datetime.now(timezone.utc),
                )
                user.usage_stats.total_sessions = 1
                user = await user_service.user_repository.create(user)

        return OAuthLoginResponseData(
            user_id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.profile.display_name,
            avatar_url=user.profile.avatar_url,
            role=user.role.value,
            status=user.status.value,
            is_new_user=is_new_user,
        )

    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}",
        )


@router.post("/{provider}/unlink/{user_id}", status_code=status.HTTP_200_OK)
@require_owner_or_admin
async def unlink_oauth_provider(
    provider: str,
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_active_user),
) -> dict:
    """Unlink OAuth provider from user account."""
    try:
        oauth_provider = OAuthProvider(provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}",
        )

    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if user has password or other OAuth providers
    other_oauth_providers = [
        oauth for oauth in user.oauth_info if oauth.provider != oauth_provider
    ]

    if not user.password_hash and len(other_oauth_providers) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unlink the only authentication method. Please set a password first.",
        )

    # Remove OAuth info for the specified provider
    user.oauth_info = other_oauth_providers
    await user_service.user_repository.update(user)

    return {"message": f"{provider.title()} account unlinked successfully"}


@router.post("/cleanup", status_code=status.HTTP_200_OK)
@require_admin
async def cleanup_oauth_states(
    oauth_service: object = Depends(get_oauth_manager),
    current_user: CurrentUser = Depends(get_current_active_user),
) -> dict:
    """Clean up expired OAuth states."""
    try:
        count = await oauth_service.cleanup_expired_states()
        return {"message": f"Cleaned up {count} expired OAuth states"}
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
