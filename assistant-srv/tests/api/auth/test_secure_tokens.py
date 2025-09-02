#!/usr/bin/env python3
"""
Test script for secure token encryption system.
"""

import os
import sys

from assistant.utils.security import TokenGenerator

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_token_encryption() -> None:
    """Test token encryption and decryption."""
    print("🔐 Testing Secure Token System...")
    print("=" * 50)

    # Test data
    session_id = "test_session_123"
    user_id = "user_456"

    print("📊 Original Data:")
    print(f"   Session ID: {session_id}")
    print(f"   User ID: {user_id}")
    print()

    # Generate secure token
    try:
        secure_token, _ = TokenGenerator.generate_jwt_token(session_id, user_id, {})
        print("🔒 Generated Secure Token:")
        print(f"   {secure_token}")
        print(f"   Length: {len(secure_token)} characters")
        print()

        # Decrypt token
        payload = TokenGenerator.decode_jwt_token(secure_token)
        if payload:
            print("🔓 Decrypted Payload:")
            for key, value in payload.items():
                print(f"   {key}: {value}")
            print()
        else:
            print("❌ Failed to decrypt token!")
            return

        # Extract session ID
        extracted_session_id = TokenGenerator.extract_session_id_from_jwt(secure_token)
        print(f"📤 Extracted Session ID: {extracted_session_id}")
        print()

        # Verify integrity
        if extracted_session_id == session_id:
            print("✅ Token encryption/decryption successful!")
            print("✅ Session ID extraction successful!")
        else:
            print("❌ Session ID mismatch!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    print()
    print("🔍 Testing Invalid Token...")

    # Test invalid token
    invalid_token = "invalid_token_12345"
    extracted = TokenGenerator.extract_session_id_from_jwt(invalid_token)
    if extracted is None:
        print("✅ Invalid token correctly rejected!")
    else:
        print("❌ Invalid token should have been rejected!")

    print()
    print("🚀 Test completed!")


if __name__ == "__main__":
    test_token_encryption()
