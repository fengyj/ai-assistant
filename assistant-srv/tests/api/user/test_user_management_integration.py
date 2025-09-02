"""
Integration test for user management module.
"""

import shutil
import tempfile
from typing import Generator

import pytest

from assistant.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from assistant.models import UserCreateRequest, UserRole, UserStatus, UserUpdateRequest
from assistant.repositories.json_user_repository import JsonUserRepository
from assistant.services.user_service import UserService


class TestUserManagementIntegration:
    """Integration tests for user management."""

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def user_service(self, temp_dir: str) -> UserService:
        """Create user service with temporary repository."""
        user_repo = JsonUserRepository(temp_dir)
        from assistant.repositories.json_session_repository import JsonSessionRepository

        session_repo = JsonSessionRepository(temp_dir)
        return UserService(user_repo, session_repo)

    @pytest.mark.asyncio
    async def test_complete_user_lifecycle(self, user_service: UserService) -> None:
        """Test complete user lifecycle: create, read, update, delete."""

        # 1. Create user
        create_request = UserCreateRequest(
            username="testuser",
            email="test@example.com",
            password="securepass123",
            display_name="Test User",
        )

        user = await user_service.create_user(create_request)

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.profile.display_name == "Test User"
        assert user.role == UserRole.USER
        assert user.status == UserStatus.ACTIVE
        assert user.password_hash is not None

        # 2. Read user
        retrieved_user = await user_service.get_user_by_id(user.id)
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"

        # 3. Authenticate user
        authenticated_user = await user_service.authenticate_user("testuser", "securepass123")
        assert authenticated_user.id == user.id
        assert authenticated_user.last_login is not None

        # 4. Update user
        update_request = UserUpdateRequest(
            display_name="Updated Test User",
            bio="This is a test user account",
            timezone="UTC",
        )

        updated_user = await user_service.update_user(user.id, update_request)
        assert updated_user.profile.display_name == "Updated Test User"
        assert updated_user.profile.bio == "This is a test user account"
        assert updated_user.profile.timezone == "UTC"

        # 5. Search users
        search_results = await user_service.search_users("test", 10)
        assert len(search_results) == 1
        assert search_results[0].username == "testuser"

        # 6. Get all users
        all_users = await user_service.get_all_users()
        assert len(all_users) == 1

        # 7. Change password
        success = await user_service.change_password(user.id, "securepass123", "newsecurepass456")
        assert success is True

        # 8. Test new password
        new_auth_user = await user_service.authenticate_user("testuser", "newsecurepass456")
        assert new_auth_user.id == user.id

        # 9. Delete user
        delete_success = await user_service.delete_user(user.id)
        assert delete_success is True

        # 10. Verify user is deleted
        deleted_user = await user_service.get_user_by_id(user.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_duplicate_user_prevention(self, user_service: UserService) -> None:
        """Test prevention of duplicate users."""

        # Create first user
        create_request1 = UserCreateRequest(username="duplicate", email="duplicate@example.com", password="password123")

        await user_service.create_user(create_request1)

        # Try to create user with same username
        create_request2 = UserCreateRequest(username="duplicate", email="different@example.com", password="password123")

        with pytest.raises(UserAlreadyExistsError):
            await user_service.create_user(create_request2)

        # Try to create user with same email
        create_request3 = UserCreateRequest(username="different", email="duplicate@example.com", password="password123")

        with pytest.raises(UserAlreadyExistsError):
            await user_service.create_user(create_request3)

    @pytest.mark.asyncio
    async def test_authentication_failures(self, user_service: UserService) -> None:
        """Test authentication failure scenarios."""

        # Create user
        create_request = UserCreateRequest(username="authtest", email="auth@example.com", password="correctpass")

        user = await user_service.create_user(create_request)

        # Test wrong password
        with pytest.raises(InvalidCredentialsError):
            await user_service.authenticate_user("authtest", "wrongpass")

        # Test non-existent user
        with pytest.raises(InvalidCredentialsError):
            await user_service.authenticate_user("nonexistent", "anypass")

        # Test inactive user
        user.status = UserStatus.INACTIVE
        await user_service.user_repository.update(user)

        with pytest.raises(InvalidCredentialsError):
            await user_service.authenticate_user("authtest", "correctpass")

    @pytest.mark.asyncio
    async def test_admin_user_creation(self, user_service: UserService) -> None:
        """Test admin user creation."""

        create_request = UserCreateRequest(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            role=UserRole.ADMIN,
        )

        admin_user = await user_service.create_user(create_request)

        assert admin_user.role == UserRole.ADMIN
        assert admin_user.username == "admin"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
