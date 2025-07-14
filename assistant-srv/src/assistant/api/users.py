"""
User API endpoints.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr

from ..models import UserCreateRequest, UserUpdateRequest, UserResponse, UserRole
from ..services.user_service import UserService
from ..repositories.json_user_repository import JsonUserRepository
from ..core.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    ValidationError
)


# Pydantic models for API
class UserCreateAPI(BaseModel):
    """User creation API model."""
    username: str
    email: EmailStr
    password: Optional[str] = None
    display_name: Optional[str] = None
    role: str = "user"


class UserUpdateAPI(BaseModel):
    """User update API model."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class LoginAPI(BaseModel):
    """Login API model."""
    username: str
    password: str


class PasswordChangeAPI(BaseModel):
    """Password change API model."""
    old_password: str
    new_password: str


class UserResponseAPI(BaseModel):
    """User response API model."""
    id: str
    username: str
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    status: str
    created_at: str
    last_login: Optional[str] = None


# Dependency injection
def get_user_service() -> UserService:
    """Get user service instance."""
    user_repository = JsonUserRepository()
    return UserService(user_repository)


# Router
router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponseAPI, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateAPI,
    user_service: UserService = Depends(get_user_service)
):
    """Create a new user."""
    try:
        # Convert API model to service model
        role = UserRole.ADMIN if user_data.role == "admin" else UserRole.USER
        request = UserCreateRequest(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.display_name,
            role=role
        )
        
        user = await user_service.create_user(request)
        user_response = UserResponse.from_user(user)
        
        return UserResponseAPI(
            id=user_response.id,
            username=user_response.username,
            email=user_response.email,
            display_name=user_response.display_name,
            avatar_url=user_response.avatar_url,
            role=user_response.role,
            status=user_response.status,
            created_at=user_response.created_at,
            last_login=user_response.last_login
        )
        
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserResponseAPI)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID."""
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user_response = UserResponse.from_user(user)
        return UserResponseAPI(
            id=user_response.id,
            username=user_response.username,
            email=user_response.email,
            display_name=user_response.display_name,
            avatar_url=user_response.avatar_url,
            role=user_response.role,
            status=user_response.status,
            created_at=user_response.created_at,
            last_login=user_response.last_login
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[UserResponseAPI])
async def get_users(
    active_only: bool = False,
    user_service: UserService = Depends(get_user_service)
):
    """Get all users."""
    try:
        if active_only:
            users = await user_service.get_active_users()
        else:
            users = await user_service.get_all_users()
        
        return [
            UserResponseAPI(
                id=user.id,
                username=user.username,
                email=user.email,
                display_name=user.profile.display_name,
                avatar_url=user.profile.avatar_url,
                role=user.role.value,
                status=user.status.value,
                created_at=user.created_at.isoformat(),
                last_login=user.last_login.isoformat() if user.last_login else None
            )
            for user in users
        ]
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{user_id}", response_model=UserResponseAPI)
async def update_user(
    user_id: str,
    user_data: UserUpdateAPI,
    user_service: UserService = Depends(get_user_service)
):
    """Update user information."""
    try:
        request = UserUpdateRequest(
            username=user_data.username,
            email=user_data.email,
            display_name=user_data.display_name,
            bio=user_data.bio,
            timezone=user_data.timezone,
            language=user_data.language
        )
        
        user = await user_service.update_user(user_id, request)
        user_response = UserResponse.from_user(user)
        
        return UserResponseAPI(
            id=user_response.id,
            username=user_response.username,
            email=user_response.email,
            display_name=user_response.display_name,
            avatar_url=user_response.avatar_url,
            role=user_response.role,
            status=user_response.status,
            created_at=user_response.created_at,
            last_login=user_response.last_login
        )
        
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """Delete a user."""
    try:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/login", response_model=UserResponseAPI)
async def login(
    login_data: LoginAPI,
    user_service: UserService = Depends(get_user_service)
):
    """Authenticate user."""
    try:
        user = await user_service.authenticate_user(login_data.username, login_data.password)
        user_response = UserResponse.from_user(user)
        
        return UserResponseAPI(
            id=user_response.id,
            username=user_response.username,
            email=user_response.email,
            display_name=user_response.display_name,
            avatar_url=user_response.avatar_url,
            role=user_response.role,
            status=user_response.status,
            created_at=user_response.created_at,
            last_login=user_response.last_login
        )
        
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/{user_id}/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    user_id: str,
    password_data: PasswordChangeAPI,
    user_service: UserService = Depends(get_user_service)
):
    """Change user password."""
    try:
        success = await user_service.change_password(
            user_id, 
            password_data.old_password, 
            password_data.new_password
        )
        return {"message": "Password changed successfully"}
        
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/search/{query}", response_model=List[UserResponseAPI])
async def search_users(
    query: str,
    limit: int = 10,
    user_service: UserService = Depends(get_user_service)
):
    """Search users by query."""
    try:
        users = await user_service.search_users(query, limit)
        
        return [
            UserResponseAPI(
                id=user.id,
                username=user.username,
                email=user.email,
                display_name=user.profile.display_name,
                avatar_url=user.profile.avatar_url,
                role=user.role.value,
                status=user.status.value,
                created_at=user.created_at.isoformat(),
                last_login=user.last_login.isoformat() if user.last_login else None
            )
            for user in users
        ]
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
