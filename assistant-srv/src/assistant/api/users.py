"""
User API endpoints.
Focused on HTTP layer concerns only, business logic delegated to services.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ..core.dependencies import get_user_service
from ..core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from ..models import UserCreateRequest, UserResponse, UserRole, UserUpdateRequest
from ..models.api.exceptions import (
    BadRequestException,
    ConflictException,
    InternalServerErrorException,
    NotFoundException,
    UnauthorizedException,
)
from ..models.api.user_api import (
    PasswordChangeRequestData,
    PasswordChangeResponseData,
    UserCreateRequestData,
    UserResponseData,
    UserRoleUpdateRequestData,
    UserRoleUpdateResponseData,
    UserUpdateRequestData,
)
from ..services.user_service import UserService
from ..utils.auth import CurrentUser, get_admin, get_owner, get_owner_or_admin

# Router
router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponseData)
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
        raise ConflictException(detail=str(e))
    except ValidationError as e:
        raise BadRequestException(detail=str(e))


@router.get("/{user_id}", response_model=UserResponseData)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_owner_or_admin),
) -> UserResponseData:
    """Get user by ID (User can access own data, Admin can access any)."""
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(detail="User not found")

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
        raise InternalServerErrorException(detail=str(e))


@router.get("/", response_model=List[UserResponseData])
async def get_users(
    active_only: bool = False,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_admin),
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
        raise InternalServerErrorException(detail=str(e))


@router.put("/{user_id}", response_model=UserResponseData)
async def update_user(
    user_id: str,
    user_data: UserUpdateRequestData,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_owner_or_admin),
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
        raise NotFoundException(detail=str(e))
    except UserAlreadyExistsError as e:
        raise ConflictException(detail=str(e))
    except ValidationError as e:
        raise BadRequestException(detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_admin),
) -> None:
    """Delete a user (Admin only)."""
    try:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    except UserNotFoundError as e:
        raise NotFoundException(detail=str(e))


@router.post("/{user_id}/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    user_id: str,
    password_data: PasswordChangeRequestData,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_owner),
) -> PasswordChangeResponseData:
    """
    Change user password (User can change own password, Admin can change any).
    """
    try:
        await user_service.change_password(user_id, password_data.old_password, password_data.new_password)
        return PasswordChangeResponseData(message="Password changed successfully")

    except UserNotFoundError as e:
        raise NotFoundException(detail=str(e))
    except InvalidCredentialsError as e:
        raise UnauthorizedException(detail=str(e))


@router.post("/{user_id}/change-role", status_code=status.HTTP_200_OK)
async def change_role(
    user_id: str,
    role_data: UserRoleUpdateRequestData,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_admin),
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
        raise NotFoundException(detail=str(e))
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))


@router.get("/search/{query}", response_model=List[UserResponseData])
async def search_users(
    query: str,
    limit: int = 10,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_admin),
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
        raise InternalServerErrorException(detail=str(e))
