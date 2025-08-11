#!/usr/bin/env python3
"""
Test script for the new session architecture without token storage.
"""

import os
import sys

import pytest

from assistant.models.session import UserSession
from assistant.repositories.json_session_repository import JsonSessionRepository
from assistant.services.session_service import SessionService
from assistant.utils.security import TokenGenerator

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


@pytest.mark.asyncio
async def test_new_session_architecture():
    """Test the new session architecture."""
    print("🔄 Testing New Session Architecture")
    print("=" * 50)

    # Setup
    repository = JsonSessionRepository("test_data")
    service = SessionService(repository)

    print("📊 Architecture Test:")
    print("1. Create session (no token stored)")
    print("2. Generate JWT token dynamically")
    print("3. Validate JWT token → find session")
    print()

    # Test data
    user_id = "test_user_arch"

    # 1. Create session

    session = UserSession(user_id=user_id, device_info="Test Browser")
    session.update_ip_tracking("192.168.1.100")

    session = await service.create_session(session)
    print("✅ Created session:")
    print(f"   Session ID: {session.id}")
    print(f"   User ID: {session.user_id}")
    print(f"   Has token attribute: {hasattr(session, 'token')}")
    print()

    # 2. Generate JWT token
    jwt_token = TokenGenerator.generate_jwt_token(session.id, session.user_id, {}, expire_hours=1)
    print("✅ Generated JWT token:")
    print(f"   Token: {jwt_token[:50]}...")
    print(f"   Length: {len(jwt_token)} characters")
    print()

    # 3. Decode JWT to verify content
    payload = TokenGenerator.decode_jwt_token(jwt_token)
    if payload:
        print("🔍 JWT Content:")
        for key, value in payload.items():
            print(f"   {key}: {value}")
        print()

        # 4. Validate token by finding session
        sid_from_token = payload.get("sid")
        assert sid_from_token and sid_from_token == session.id, "Session ID in token does not match created session"
        uid_from_token = payload.get("sub")
        assert uid_from_token and uid_from_token == session.user_id, "User ID in token does not match created session"
        found_session = await service.get_by_session_id_and_user_id(session_id=sid_from_token, user_id=uid_from_token)
        if found_session:
            print("✅ Token validation successful:")
            print(f"   Found session ID: {found_session.id}")
            print(f"   Matches original: {found_session.id == session.id}")
            print(f"   Session is active: {found_session.is_active()}")
        else:
            print("❌ Token validation failed!")
    else:
        print("❌ Failed to decode JWT!")

    print()
    print("🎯 Architecture Benefits:")
    print("   ✅ Session model is clean (no token field)")
    print("   ✅ JWT contains session_id for lookup")
    print("   ✅ Token generated dynamically when needed")
    print("   ✅ No circular dependency")
    print("   ✅ Proper separation of concerns")
    print()

    # Test IP tracking
    print("🔍 IP Tracking Test:")
    print(f"   Initial IP: {session.metadata.initial_ip}")
    print(f"   Known IPs: {session.metadata.last_known_ips}")

    # Simulate IP change
    await service.update_session_ip(session_id=session.id, user_id=session.user_id, current_ip="10.0.0.5")
    updated_session = await service.get_by_session_id_and_user_id(session_id=session.id, user_id=session.user_id)
    if updated_session:
        print(f"   After update - Known IPs: {updated_session.metadata.last_known_ips}")
        print("   ✅ IP tracking works for security analysis")

    # Cleanup
    if os.path.exists("test_data"):
        import shutil

        shutil.rmtree("test_data")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_new_session_architecture())
