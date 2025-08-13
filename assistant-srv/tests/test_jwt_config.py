#!/usr/bin/env python3
"""
Test script for JWT configuration.
"""

import os
import sys

from assistant.core.config import config
from assistant.utils.security import TokenGenerator

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_jwt_configuration():
    """Test JWT configuration settings."""
    print("🔧 JWT Configuration Test")
    print("=" * 40)

    # Display current configuration
    print("📊 Current JWT Settings:")
    print(f"   Issuer: {config.jwt_issuer}")
    print(f"   Algorithm: {config.jwt_algorithm}")
    print(f"   JWT Secret Key: {config.jwt_secret_key[:10]}...")
    print()

    # Test data
    session_id = "test_session_456"
    user_id = "test_user_789"

    print("🧪 Generating JWT with configuration...")

    try:
        # Generate JWT token
        jwt_token = TokenGenerator.generate_jwt_token(session_id, user_id, {})
        print(f"✅ Generated JWT: {jwt_token[:50]}...")
        print(f"   Length: {len(jwt_token)} characters")
        print()

        # Decode JWT to verify configuration
        payload = TokenGenerator.decode_jwt_token(jwt_token)
        if payload:
            print("🔍 JWT Payload:")
            for key, value in payload.items():
                print(f"   {key}: {value}")
            print()

            # Verify issuer from config
            expected_issuer = config.jwt_issuer
            actual_issuer = payload.get("iss")

            if actual_issuer == expected_issuer:
                print("✅ Issuer verification: SUCCESS")
                print(f"   Expected: {expected_issuer}")
                print(f"   Actual: {actual_issuer}")
            else:
                print("❌ Issuer verification: FAILED")
                print(f"   Expected: {expected_issuer}")
                print(f"   Actual: {actual_issuer}")

            print()

            # Test session ID extraction
            extracted_sid = TokenGenerator.extract_session_id_from_jwt(jwt_token)
            if extracted_sid == session_id:
                print("✅ Session ID extraction: SUCCESS")
            else:
                print("❌ Session ID extraction: FAILED")

        else:
            print("❌ Failed to decode JWT!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    print()
    print("🎯 Configuration Benefits:")
    print("   ✅ Issuer can be customized per environment")
    print("   ✅ Algorithm can be changed if needed")
    print("   ✅ No hardcoded values in source code")
    print("   ✅ Production/development isolation")


def test_custom_issuer():
    """Test with custom issuer."""
    print("\n" + "=" * 40)
    print("🏢 Custom Issuer Test")
    print("=" * 40)

    # Temporarily modify config for test
    original_issuer = config.jwt_issuer
    config.jwt_issuer = "my-custom-app-v2"

    try:
        jwt_token = TokenGenerator.generate_jwt_token("test_session", "test_user")
        payload = TokenGenerator.decode_jwt_token(jwt_token)

        if payload and payload.get("iss") == "my-custom-app-v2":
            print("✅ Custom issuer test: SUCCESS")
            print(f"   Custom issuer: {payload.get('iss')}")
        else:
            print("❌ Custom issuer test: FAILED")

    finally:
        # Restore original issuer
        config.jwt_issuer = original_issuer


if __name__ == "__main__":
    test_jwt_configuration()
    test_custom_issuer()
