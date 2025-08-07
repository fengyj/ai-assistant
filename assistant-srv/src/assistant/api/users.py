"""
User API endpoints.
Focused on HTTP layer concerns only, business logic delegated to services.
"""

from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ..core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from ..models import UserCreateRequest, UserResponse, UserRole, UserUpdateRequest
from ..models.api.user_api import (
    LoginRequestData,
    OAuthLoginRequestData,
    PasswordChangeRequestData,
    PasswordChangeResponseData,
    TokenResponseData,
    UserCreateRequestData,
    UserResponseData,
    UserRoleUpdateRequestData,
    UserRoleUpdateResponseData,
    UserUpdateRequestData,
)
from ..repositories.json_user_repository import JsonUserRepository
from ..services.user_service import UserService
from ..utils.auth import CurrentUser, create_access_token, get_current_user
from ..utils.permissions import require_admin, require_owner, require_owner_or_admin


# Dependency injection
def get_user_service() -> UserService:
    """Get user service instance."""
    user_repository = JsonUserRepository()
    return UserService(user_repository)


# Router
router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponseData, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequestData,
    user_service: UserService = Depends(get_user_service),
) -> UserResponseData:
    """Create a new normal user."""
    try:
        # Convert API model to service model
        request = UserCreateRequest(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.display_name,
            role=UserRole.USER,
        )

        user = await user_service.create_user(request)
        user_response = UserResponse.from_user(user)

        return UserResponseData(
            id=user_response.id,
            username=user_response.username,
            email=user_response.email,
            display_name=user_response.display_name,
            avatar_url=user_response.avatar_url,
            role=user_response.role,
            status=user_response.status,
            created_at=user_response.created_at,
            last_login=user_response.last_login,
        )

    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserResponseData)
@require_owner_or_admin
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> UserResponseData:
    """Get user by ID (User can access own data, Admin can access any)."""
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user_response = UserResponse.from_user(user)
        return UserResponseData(
            id=user_response.id,
            username=user_response.username,
            email=user_response.email,
            display_name=user_response.display_name,
            avatar_url=user_response.avatar_url,
            role=user_response.role,
            status=user_response.status,
            created_at=user_response.created_at,
            last_login=user_response.last_login,
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[UserResponseData])
@require_admin
async def get_users(
    active_only: bool = False,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> List[UserResponseData]:
    """Get all users (Admin only)."""
    try:
        if active_only:
            users = await user_service.get_active_users()
        else:
            users = await user_service.get_all_users()

        return [
            UserResponseData(
                id=user.id,
                username=user.username,
                email=user.email,
                display_name=user.profile.display_name,
                avatar_url=user.profile.avatar_url,
                role=user.role.value,
                status=user.status.value,
                created_at=user.created_at.isoformat(),
                last_login=(user.last_login.isoformat() if user.last_login else None),
            )
            for user in users
        ]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{user_id}", response_model=UserResponseData)
@require_owner_or_admin
async def update_user(
    user_id: str,
    user_data: UserUpdateRequestData,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> UserResponseData:
    """
    Update user information (User can update own data, Admin can update any).
    """
    try:
        request = UserUpdateRequest(
            username=user_data.username,
            display_name=user_data.display_name,
            bio=user_data.bio,
            timezone=user_data.timezone,
            language=user_data.language,
        )

        user = await user_service.update_user(user_id, request)
        user_response = UserResponse.from_user(user)

        return UserResponseData(
            id=user_response.id,
            username=user_response.username,
            email=user_response.email,
            display_name=user_response.display_name,
            avatar_url=user_response.avatar_url,
            role=user_response.role,
            status=user_response.status,
            created_at=user_response.created_at,
            last_login=user_response.last_login,
        )

    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_admin
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """Delete a user (Admin only)."""
    try:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/login", response_model=TokenResponseData)
async def login(
    login_data: LoginRequestData, user_service: UserService = Depends(get_user_service)
) -> TokenResponseData:
    """Authenticate user and return access token."""
    try:
        user = await user_service.authenticate_user(login_data.username, login_data.password)
        user_response = UserResponse.from_user(user)

        # Create access token
        access_token = create_access_token(
            data={"sub": user.id, "username": user.username},
            expires_delta=timedelta(minutes=30),
        )

        user_api = UserResponseData(
            id=user_response.id,
            username=user_response.username,
            email=user_response.email,
            display_name=user_response.display_name,
            avatar_url=user_response.avatar_url,
            role=user_response.role,
            status=user_response.status,
            created_at=user_response.created_at,
            last_login=user_response.last_login,
        )

        return TokenResponseData(access_token=access_token, token_type="bearer", user=user_api)

    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/oauth-login", response_model=TokenResponseData)
async def oauth_login(
    oauth_data: OAuthLoginRequestData, user_service: UserService = Depends(get_user_service)
) -> TokenResponseData:
    """OAuth login - create user if not exists, login if exists."""
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

        user_response = UserResponse.from_user(user)

        # Create access token
        access_token = create_access_token(
            data={"sub": user.id, "username": user.username},
            expires_delta=timedelta(minutes=30),
        )

        user_api = UserResponseData(
            id=user_response.id,
            username=user_response.username,
            email=user_response.email,
            display_name=user_response.display_name,
            avatar_url=user_response.avatar_url,
            role=user_response.role,
            status=user_response.status,
            created_at=user_response.created_at,
            last_login=user_response.last_login,
        )

        return TokenResponseData(access_token=access_token, token_type="bearer", user=user_api)

    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth login failed: {str(e)}",
        )


@router.post("/{user_id}/change-password", status_code=status.HTTP_200_OK)
@require_owner
async def change_password(
    user_id: str,
    password_data: PasswordChangeRequestData,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> PasswordChangeResponseData:
    """
    Change user password (User can change own password, Admin can change any).
    """
    try:
        await user_service.change_password(user_id, password_data.old_password, password_data.new_password)
        return PasswordChangeResponseData(message="Password changed successfully")

    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/{user_id}/change-role", status_code=status.HTTP_200_OK)
@require_admin
async def change_role(
    user_id: str,
    role_data: UserRoleUpdateRequestData,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> UserRoleUpdateResponseData:
    """
    Change user role (Admin only).
    """
    try:
        await user_service.change_user_role(
            current_user.id, user_id, UserRole.from_str(role_data.new_role), role_data.reason
        )
        return UserRoleUpdateResponseData(message="User role changed successfully")

    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/search/{query}", response_model=List[UserResponseData])
@require_admin
async def search_users(
    query: str,
    limit: int = 10,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> List[UserResponseData]:
    """Search users by query (Admin only)."""
    try:
        users = await user_service.search_users(query, limit)

        return [
            UserResponseData(
                id=user.id,
                username=user.username,
                email=user.email,
                display_name=user.profile.display_name,
                avatar_url=user.profile.avatar_url,
                role=user.role.value,
                status=user.status.value,
                created_at=user.created_at.isoformat(),
                last_login=(user.last_login.isoformat() if user.last_login else None),
            )
            for user in users
        ]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
