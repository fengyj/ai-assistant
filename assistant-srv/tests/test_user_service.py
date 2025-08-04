"""
Test cases for user service.
"""

import pytest
from datetime import datetime
from assistant.models import (
    User,
    UserCreateRequest,
    UserUpdateRequest,
    UserRole,
    UserStatus,
)
from assistant.repositories.json_user_repository import JsonUserRepository
from assistant.services.user_service import UserService
from assistant.core.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
)


class TestUserService:
    """Test user service."""

    @pytest.fixture
    def user_service(self, tmp_path):
        """Create user service with temporary repository."""
        repo = JsonUserRepository(str(tmp_path))
        return UserService(repo)

    @pytest.mark.asyncio
    async def test_create_user(self, user_service):
        """Test user creation."""
        request = UserCreateRequest(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            display_name="Test User",
        )

        user = await user_service.create_user(request)

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.profile.display_name == "Test User"
        assert user.role == UserRole.USER
        assert user.status == UserStatus.ACTIVE
        assert user.password_hash is not None

    @pytest.mark.asyncio
    async def test_create_duplicate_user(self, user_service):
        """Test creating duplicate user."""
        request = UserCreateRequest(
            username="testuser", email="test@example.com", password="testpass123"
        )

        await user_service.create_user(request)

        with pytest.raises(UserAlreadyExistsError):
            await user_service.create_user(request)

    @pytest.mark.asyncio
    async def test_authenticate_user(self, user_service):
        """Test user authentication."""
        request = UserCreateRequest(
            username="testuser", email="test@example.com", password="testpass123"
        )

        created_user = await user_service.create_user(request)

        # Test successful authentication
        authenticated_user = await user_service.authenticate_user(
            "testuser", "testpass123"
        )
        assert authenticated_user.id == created_user.id
        assert authenticated_user.last_login is not None

    @pytest.mark.asyncio
    async def test_authenticate_invalid_credentials(self, user_service):
        """Test authentication with invalid credentials."""
        request = UserCreateRequest(
            username="testuser", email="test@example.com", password="testpass123"
        )

        await user_service.create_user(request)

        # Test invalid password
        with pytest.raises(InvalidCredentialsError):
            await user_service.authenticate_user("testuser", "wrongpass")

        # Test invalid username
        with pytest.raises(InvalidCredentialsError):
            await user_service.authenticate_user("wronguser", "testpass123")

    @pytest.mark.asyncio
    async def test_update_user(self, user_service):
        """Test user update."""
        request = UserCreateRequest(
            username="testuser", email="test@example.com", password="testpass123"
        )

        user = await user_service.create_user(request)

        update_request = UserUpdateRequest(
            display_name="Updated Name", bio="Updated bio"
        )

        updated_user = await user_service.update_user(user.id, update_request)

        assert updated_user.profile.display_name == "Updated Name"
        assert updated_user.profile.bio == "Updated bio"

    @pytest.mark.asyncio
    async def test_delete_user(self, user_service):
        """Test user deletion."""
        request = UserCreateRequest(
            username="testuser", email="test@example.com", password="testpass123"
        )

        user = await user_service.create_user(request)

        # Test successful deletion
        success = await user_service.delete_user(user.id)
        assert success is True

        # Test user no longer exists
        deleted_user = await user_service.get_user_by_id(user.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_change_password(self, user_service):
        """Test password change."""
        request = UserCreateRequest(
            username="testuser", email="test@example.com", password="testpass123"
        )

        user = await user_service.create_user(request)

        # Test successful password change
        success = await user_service.change_password(
            user.id, "testpass123", "newpass456"
        )
        assert success is True

        # Test authentication with new password
        authenticated_user = await user_service.authenticate_user(
            "testuser", "newpass456"
        )
        assert authenticated_user.id == user.id

        # Test old password no longer works
        with pytest.raises(InvalidCredentialsError):
            await user_service.authenticate_user("testuser", "testpass123")
