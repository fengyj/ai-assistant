"""
User service layer for business logic.
"""

from datetime import datetime, timezone
from typing import Optional, List
from ..core.exceptions import (
    UserNotFoundError, 
    UserAlreadyExistsError, 
    InvalidCredentialsError,
    ValidationError
)
from ..models import User, UserCreateRequest, UserUpdateRequest, UserRole, UserStatus
from ..repositories.user_repository import UserRepository
from ..utils.security import PasswordHasher


class UserService:
    """User service for business logic."""
    
    def __init__(self, user_repository: UserRepository):
        """Initialize user service."""
        self.user_repository = user_repository
        self.password_hasher = PasswordHasher()
    
    async def create_user(self, request: UserCreateRequest) -> User:
        """Create a new user."""
        # Validate input
        if not request.username or not request.email:
            raise ValidationError("Username and email are required")
        
        if not request.password and not request.role == UserRole.ADMIN:
            raise ValidationError("Password is required for regular users")
        
        # Check if user already exists
        if await self.user_repository.get_by_username(request.username):
            raise UserAlreadyExistsError(f"Username {request.username} already exists")
        
        if await self.user_repository.get_by_email(request.email):
            raise UserAlreadyExistsError(f"Email {request.email} already exists")
        
        # Create user
        user = User(
            username=request.username,
            email=request.email,
            password_hash=self.password_hasher.hash_password(request.password) if request.password else None,
            role=request.role,
            status=UserStatus.ACTIVE
        )
        
        # Set display name
        if request.display_name:
            user.profile.display_name = request.display_name
        
        return await self.user_repository.create(user)
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repository.get_by_id(user_id)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return await self.user_repository.get_by_username(username)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.user_repository.get_by_email(email)
    
    async def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate user with username and password."""
        user = await self.user_repository.get_by_username(username)
        
        if not user:
            raise InvalidCredentialsError("Invalid username or password")
        
        if not user.password_hash:
            raise InvalidCredentialsError("Password authentication not available for this user")
        
        if not self.password_hasher.verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid username or password")
        
        if user.status != UserStatus.ACTIVE:
            raise InvalidCredentialsError("User account is not active")
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        user.usage_stats.total_sessions += 1
        await self.user_repository.update(user)
        
        return user
    
    async def update_user(self, user_id: str, request: UserUpdateRequest) -> User:
        """Update user information."""
        user = await self.user_repository.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        # Update fields
        if request.username is not None:
            # Check username uniqueness
            existing_user = await self.user_repository.get_by_username(request.username)
            if existing_user and existing_user.id != user_id:
                raise UserAlreadyExistsError(f"Username {request.username} already exists")
            user.username = request.username
        
        if request.email is not None:
            # Check email uniqueness
            existing_user = await self.user_repository.get_by_email(request.email)
            if existing_user and existing_user.id != user_id:
                raise UserAlreadyExistsError(f"Email {request.email} already exists")
            user.email = request.email
        
        if request.display_name is not None:
            user.profile.display_name = request.display_name
        
        if request.bio is not None:
            user.profile.bio = request.bio
        
        if request.timezone is not None:
            user.profile.timezone = request.timezone
        
        if request.language is not None:
            user.profile.language = request.language
        
        if request.preferences is not None:
            user.profile.preferences.update(request.preferences)
        
        return await self.user_repository.update(user)
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        user = await self.user_repository.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return await self.user_repository.delete(user_id)
    
    async def get_all_users(self) -> List[User]:
        """Get all users."""
        return await self.user_repository.get_all()
    
    async def get_active_users(self) -> List[User]:
        """Get all active users."""
        return await self.user_repository.get_active_users()
    
    async def search_users(self, query: str, limit: int = 10) -> List[User]:
        """Search users by query."""
        return await self.user_repository.search_users(query, limit)
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password."""
        user = await self.user_repository.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        if not user.password_hash:
            raise InvalidCredentialsError("Password authentication not available for this user")
        
        if not self.password_hasher.verify_password(old_password, user.password_hash):
            raise InvalidCredentialsError("Invalid current password")
        
        user.password_hash = self.password_hasher.hash_password(new_password)
        await self.user_repository.update(user)
        
        return True
    
    async def update_user_activity(self, user_id: str, api_calls: int = 0, tokens: int = 0) -> bool:
        """Update user activity statistics."""
        user = await self.user_repository.get_by_id(user_id)
        
        if not user:
            return False
        
        user.usage_stats.api_calls_count += api_calls
        user.usage_stats.tokens_consumed += tokens
        user.usage_stats.last_activity = datetime.now(timezone.utc)
        
        await self.user_repository.update(user)
        return True
