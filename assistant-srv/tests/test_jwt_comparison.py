#!/usr/bin/env python3
"""
Test script comparing JWT vs Fernet token systems.
"""

import os
import sys

from assistant.utils.security import TokenGenerator

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_jwt_vs_fernet():
    """Compare JWT and Fernet token systems."""
    print("🆚 JWT vs Fernet Token Comparison")
    print("=" * 60)

    # Test data
    session_id = "session_abc123"
    user_id = "user_456789"

    print("📊 Test Data:")
    print(f"   Session ID: {session_id}")
    print(f"   User ID: {user_id}")
    print()

    # Test JWT Token
    print("🔸 JWT Token:")
    print("-" * 30)

    try:
        jwt_token = TokenGenerator.generate_jwt_token(session_id, user_id)
        print(f"Generated: {jwt_token}")
        print(f"Length: {len(jwt_token)} characters")

        # Decode JWT to show content (this is JWT's advantage!)
        jwt_payload = TokenGenerator.decode_jwt_token(jwt_token)
        if jwt_payload:
            print("Content (readable):")
            for key, value in jwt_payload.items():
                print(f"   {key}: {value}")

        # Extract session ID
        extracted_sid = TokenGenerator.extract_session_id_from_jwt(jwt_token)
        print(f"Extracted Session ID: {extracted_sid}")
        print(f"✅ JWT extraction: {'SUCCESS' if extracted_sid == session_id else 'FAILED'}")

    except Exception as e:
        print(f"❌ JWT Error: {e}")

    print()

    # Test Legacy Fernet Token for comparison
    print("🔸 Legacy Fernet Token:")
    print("-" * 30)

    try:
        # Create a legacy Fernet token manually for comparison
        fernet_payload = {
            "session_id": session_id,
            "user_id": user_id,
            "issued_at": "2025-08-08T08:15:06+00:00",
            "random": "abc123",
        }

        import base64
        import hashlib
        import json

        from cryptography.fernet import Fernet

        # Simulate legacy Fernet encryption
        secret_key = "your-session-secret-key-change-this-in-production-32bytes!"
        key = hashlib.sha256(secret_key.encode()).digest()
        fernet = Fernet(base64.urlsafe_b64encode(key))

        payload_json = json.dumps(fernet_payload, separators=(",", ":"))
        encrypted_token = fernet.encrypt(payload_json.encode("utf-8"))
        fernet_token = base64.urlsafe_b64encode(encrypted_token).decode("ascii").rstrip("=")

        print(f"Generated: {fernet_token}")
        print(f"Length: {len(fernet_token)} characters")
        print("Content: (encrypted, not readable)")

        # Extract session ID using legacy method
        extracted_sid_fernet = TokenGenerator._extract_session_id_fernet(fernet_token)
        print(f"Extracted Session ID: {extracted_sid_fernet}")
        print(f"✅ Fernet extraction: {'SUCCESS' if extracted_sid_fernet == session_id else 'FAILED'}")

    except Exception as e:
        print(f"❌ Fernet Error: {e}")

    print()
    print("🎯 Comparison Summary:")
    print("-" * 30)
    print("📏 Size: JWT (~200 chars) vs Fernet (~330 chars)")
    print("🔍 Readability: JWT ✅ (debuggable) vs Fernet ❌ (encrypted)")
    print("🏭 Standards: JWT ✅ (RFC 7519) vs Fernet ❌ (custom)")
    print("🛠️ Ecosystem: JWT ✅ (rich) vs Fernet ❌ (limited)")
    print("🔒 Security: JWT ✅ (signed) vs Fernet ✅ (encrypted)")
    print()
    print("💡 Recommendation: JWT is better for this use case!")


if __name__ == "__main__":
    test_jwt_vs_fernet()
