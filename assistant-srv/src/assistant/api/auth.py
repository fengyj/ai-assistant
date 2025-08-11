"""
Authentication API endpoints.
Handles token refresh and advanced authentication operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Request

from ..core.config import config

# Import centralized dependencies
from ..core.dependencies import get_session_service, get_user_service
from ..core.exceptions import InvalidCredentialsError
from ..models.api.auth_api import (
    LoginRequestData,
    LoginResponseData,
    LogoutResponseData,
    RefreshTokenRequestData,
    RefreshTokenResponseData,
)
from ..models.api.exceptions import InternalServerErrorException, UnauthorizedException
from ..models.api.user_api import UserResponseData
from ..models.session import UserSession  # Import UserStatus enum
from ..models.user import UserStatus

# Project internal imports
from ..services.session_service import SessionService
from ..services.user_service import UserService
from ..utils.auth import CurrentUser, get_current_user
from ..utils.security import TokenGenerator

# Router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponseData)
async def login(
    login_data: LoginRequestData,
    request: Request,
    user_service: UserService = Depends(get_user_service),
    session_service: SessionService = Depends(get_session_service),
) -> LoginResponseData:
    """Authenticate user and create session with JWT token."""
    try:
        # Authenticate user
        user = await user_service.authenticate_user(login_data.username, login_data.password)

        # Extract client information from request
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Create session (directly construct UserSession)
        session = UserSession(
            user_id=user.id,
            user_agent=user_agent,
            device_info="Web Browser",
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
            "permissions": getattr(user, "permissions", []),
        }

        # Generate JWT token with user info (15 minutes expiration)
        jwt_token = TokenGenerator.generate_jwt_token(
            session.id, user.id, user_info, expire_hours=config.jwt_expire_hours
        )

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

        return LoginResponseData(
            access_token=jwt_token, token_type="Bearer", user=user_data, expires_in=int(config.jwt_expire_hours * 3600)
        )

    except InvalidCredentialsError as e:
        raise UnauthorizedException(detail=str(e))


@router.post("/refresh", response_model=RefreshTokenResponseData)
async def refresh_access_token(
    request: RefreshTokenRequestData,
    http_request: Request,
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> RefreshTokenResponseData:
    """
    Refresh access token using session ID.

    This endpoint validates the session (refresh token) and generates a new short-lived
    access token with updated user information.
    """
    try:
        # 1. Validate session (this is our refresh token)
        session = await session_service.get_by_session_id_and_user_id(current_user.session_id, current_user.id)
        if not session or session.is_expired():
            raise UnauthorizedException(detail="Session expired or invalid")

        # 2. Get current user info for JWT payload
        user = await user_service.get_user_by_id(session.user_id)
        if not user or user.status != UserStatus.ACTIVE:
            raise UnauthorizedException(detail="User not found or inactive")

        # 3. Optionally extend session expiration (sliding window)
        if request.extend_session:
            # Use refresh_session method which extends expiration
            updated_session = await session_service.refresh_session(
                session.id, current_user.id, extend_hours=24  # Simple token format for session lookup
            )
            if updated_session:
                session = updated_session

        # 4. Update session access tracking
        if http_request.client and session:
            session.update_ip_tracking(http_request.client.host)
            await session_service.session_repository.update(session)

        # 5. Prepare user info for JWT (filter sensitive data)
        user_info = {
            "username": user.username,
            "display_name": user.profile.display_name if user.profile.display_name else user.username,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "permissions": getattr(user, "permissions", []),
        }

        # 6. Generate new access token with user info (15 minutes)
        new_access_token = TokenGenerator.generate_jwt_token(
            session.id, user.id, user_info, expire_hours=config.jwt_expire_hours
        )

        return RefreshTokenResponseData(
            access_token=new_access_token, expires_in=int(config.jwt_expire_hours * 3600), session_id=session.id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise InternalServerErrorException(detail=f"Token refresh failed: {str(e)}")


@router.post("/logout")
async def logout(
    current_user: CurrentUser = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> LogoutResponseData:
    """
    Logout user by terminating the current session.
    """
    try:
        await session_service.terminate_session(current_user.session_id, current_user.id)

        return LogoutResponseData(message="Successfully logged out")

    except Exception as e:
        raise InternalServerErrorException(detail=f"Logout failed: {str(e)}")
