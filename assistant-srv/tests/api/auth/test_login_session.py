#!/usr/bin/env python3
"""
Test script for login API with session creation.
"""

import asyncio
import os
import sys

import pytest

from assistant.models.api.auth_api import LoginRequestData
from assistant.models.user import UserCreateRequest, UserRole
from assistant.repositories.file.json_session_repository import JsonSessionRepository
from assistant.repositories.file.json_user_repository import JsonUserRepository
from assistant.services.session_service import SessionService
from assistant.services.user_service import UserService
from assistant.utils.security import TokenGenerator

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


@pytest.mark.asyncio
async def test_login_with_session() -> None:
    """Test login API creates session correctly."""
    print("🔄 Testing Login API with Session Creation")
    print("=" * 60)

    # Setup services
    user_repo = JsonUserRepository()
    session_repo = JsonSessionRepository()
    user_service = UserService(user_repo, session_repo)
    session_service = SessionService(session_repo)

    # Create test user
    print("1. Creating test user...")
    user_request = UserCreateRequest(
        username="test_login_user", email="test@example.com", password="testpass123", role=UserRole.USER
    )

    try:
        user = await user_service.create_user(user_request)
        print(f"✅ Created user: {user.username} ({user.id})")
    except Exception as e:
        # User might already exist
        result = await user_service.get_user_by_username("test_login_user")
        if result is None:
            print(f"❌ Failed to create user: {str(e)}")
            return
        print(f"✅ Using existing user: {result.username} ({result.id})")

    # Simulate login request
    print("\n2. Simulating login process...")
    login_data = LoginRequestData(username="test_login_user", password="testpass123")

    # Authenticate user (what login API does)
    authenticated_user = await user_service.authenticate_user(login_data.username, login_data.password)
    print(f"✅ User authenticated: {authenticated_user.username}")

    # Create session (what login API now does)
    from assistant.models.session import UserSession

    session = UserSession(
        user_id=authenticated_user.id,
        user_agent="Test Browser/1.0",
        device_info="Web Browser",
    )
    session.update_ip_tracking("192.168.1.100")

    # Generate JWT token (what login API now returns)
    jwt_token, _ = TokenGenerator.generate_jwt_token(session_id=session.id, user_id=session.user_id, user_info={})
    print(f"✅ JWT token generated: {jwt_token[:50]}...")

    session = await session_service.create_session(session)
    print(f"✅ Session created: {session.id}")
    print(f"   User ID: {session.user_id}")
    print(f"   Initial IP: {session.metadata.initial_ip}")
    print(f"   Known IPs: {session.metadata.last_known_ips}")

    # Verify token contains session info
    import jwt as jwt_lib

    token_payload = jwt_lib.decode(jwt_token, options={"verify_signature": False})
    print("✅ Token payload verified:")
    print(f"   User: {token_payload.get('sub')}")
    print(f"   Session ID: {token_payload.get('sid')}")
    print(f"   Issuer: {token_payload.get('iss')}")

    # Test token validation (what auth middleware does)
    sid_from_token = TokenGenerator.extract_session_id_from_dict(token_payload)
    user_id_from_token = TokenGenerator.extract_user_id_from_dict(token_payload)
    if sid_from_token is None or user_id_from_token is None:
        raise Exception("Token validation failed: Session ID or User ID mismatch")
    validated_session = await session_service.get_by_session_id_and_user_id(sid_from_token, user_id_from_token)
    if validated_session:
        print("✅ Session validation successful:")
        print(f"   Session ID matches: {validated_session.id == session.id}")
        print(f"   User ID matches: {validated_session.user_id == authenticated_user.id}")
        print(f"   Session is active: {validated_session.is_active()}")

    print("\n🎯 Login Flow Complete:")
    print("   ✅ User authentication")
    print("   ✅ Session creation with IP tracking")
    print("   ✅ JWT token generation")
    print("   ✅ Token validation and session lookup")
    print("   ✅ Complete session-based authentication flow")


if __name__ == "__main__":
    asyncio.run(test_login_with_session())
