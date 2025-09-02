"""
OAuth authentication API endpoints.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status

# Import centralized dependencies
from ..core.dependencies import get_session_service, get_user_service
from ..core.exceptions import UserAlreadyExistsError, UserNotFoundError
from ..models.api.oauth_api import OAuthLoginRequestData  # Import the missing type
from ..models.api.oauth_api import (
    OAuthCleanupResponseData,
    OAuthLoginResponseData,
    OAuthProvidersResponseData,
)
from ..models.api.user_api import UserResponseData
from ..models.session import UserSession
from ..models.user import UserCreateRequest, UserRole, UserUpdateRequest
from ..services.oauth_service import OAuthServiceManager, oauth_manager
from ..services.session_service import SessionService
from ..services.user_service import UserService
from ..utils.auth import CurrentUser, get_current_user
from ..utils.security import TokenGenerator


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


@router.post("/login", response_model=OAuthLoginResponseData)
async def oauth_login(
    oauth_data: OAuthLoginRequestData,
    request: Request,
    user_service: UserService = Depends(get_user_service),
    session_service: SessionService = Depends(get_session_service),
) -> OAuthLoginResponseData:
    """OAuth login - create user if not exists, login if exists, and create session."""
    try:
        # Try to find existing user by email
        existing_user = None
        try:
            existing_user = await user_service.get_user_by_email(oauth_data.email)
        except UserNotFoundError:
            pass

        if existing_user:
            # Update OAuth info for existing user
            if oauth_data.display_name:
                existing_user.profile.display_name = oauth_data.display_name
            if oauth_data.avatar:
                existing_user.profile.avatar_url = oauth_data.avatar
            existing_user.last_login = datetime.now(timezone.utc)

            # Update user
            await user_service.update_user(
                existing_user.id,
                UserUpdateRequest(
                    display_name=existing_user.profile.display_name,
                    avatar_url=existing_user.profile.avatar_url,
                ),
            )

            user = existing_user
        else:
            # Create new user for OAuth
            user_create = UserCreateRequest(
                username=oauth_data.username,
                email=oauth_data.email,
                display_name=oauth_data.display_name,
                role=UserRole.USER,  # Default role for OAuth users
                is_oauth=True,  # OAuth user flag
            )

            user = await user_service.create_user(user_create)

            # Update avatar separately if provided
            if oauth_data.avatar:
                await user_service.update_user(user.id, UserUpdateRequest(avatar_url=oauth_data.avatar))

        # Extract client information from request
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Create session (directly construct UserSession)
        session = UserSession(
            user_id=user.id,
            user_agent=user_agent,
            device_info="OAuth Login",
        )
        # Set up IP tracking if provided
        if ip_address:
            session.update_ip_tracking(ip_address)
        # Save session
        session = await session_service.create_session(session)

        # Prepare user info for JWT (include non-sensitive fields)
        user_info = {
            "username": user.username,
            "display_name": user.profile.display_name if user.profile.display_name else user.username,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "status": user.status.value if hasattr(user.status, "value") else str(user.status),
            "email": user.email,
            "permissions": getattr(user, "permissions", []),
        }

        # Generate JWT token with user info (15 minutes expiration)
        jwt_token, _ = TokenGenerator.generate_jwt_token(session.id, user.id, user_info)

        user_data = UserResponseData(
            id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.profile.display_name,
            avatar_url=user.profile.avatar_url,
            role=user.role.name,
            status=user.status.name,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None,
        )
        is_new_user = existing_user is None
        return OAuthLoginResponseData(
            access_token=jwt_token, token_type="Bearer", user=user_data, is_new_user=is_new_user
        )

    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth login failed: {str(e)}",
        )
