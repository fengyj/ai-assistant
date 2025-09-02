"""
Test new security endpoints for email and role changes.
"""

import time

from fastapi.testclient import TestClient

from assistant.main import app

client = TestClient(app)


def test_security_endpoints() -> None:
    """Test email change and role change endpoints."""

    print("=== Security Endpoints Test ===\n")

    # Step 1: Login as admin
    print("1. Logging in as admin...")
    admin_login = {"username": "admin", "password": "admin123"}

    response = client.post("/api/auth/login", json=admin_login)
    admin_auth = response.json()
    assert "access_token" in admin_auth, f"Login failed, response: {admin_auth}"
    admin_token = admin_auth["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    admin_id = admin_auth["user"]["id"]

    print("   Admin logged in successfully")

    # Step 2: Create a test user
    print("\n2. Creating a test user...")
    unique_username = f"securitytest_{int(time.time())}"
    test_user_data = {
        "username": unique_username,
        "email": f"{unique_username}@example.com",
        "password": "testpass123",
        "display_name": "Security Test User",
    }

    response = client.post("/api/users/", json=test_user_data, headers=admin_headers)

    if response.status_code == 201:
        user_data = response.json()
        user_id = user_data["id"]
        print(f"   Created user: {user_data['username']} (ID: {user_id})")
    else:
        print(f"   Error creating user: {response.json()}")
        return

    # Step 3: Login as the test user
    print("\n3. Logging in as test user...")
    user_login = {"username": unique_username, "password": "testpass123"}

    response = client.post("/api/auth/login", json=user_login)
    user_auth = response.json()
    user_token = user_auth["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    print(f"   User logged in: {user_auth['user']['username']}")

    # Step 4: Test email change (user tries to change own email)
    print("\n4. Testing email change...")
    email_change = {
        "new_email": f"{unique_username}.new@example.com",
        "password": "testpass123",
    }

    response = client.post(
        f"/api/users/{user_id}/change-email",
        json=email_change,
        headers=user_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Success: {response.json()['message']}")
    else:
        print(f"   Error: {response.json()}")

    # Step 5: Test email change with wrong password
    print("\n5. Testing email change with wrong password...")
    email_change_wrong = {
        "new_email": f"{unique_username}.wrong@example.com",
        "password": "wrongpassword",
    }

    response = client.post(
        f"/api/users/{user_id}/change-email",
        json=email_change_wrong,
        headers=user_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Expected error: {response.json()['detail']}")

    # Step 6: Test user trying to change admin's email (should fail)
    print("\n6. Testing user trying to change admin's email...")
    email_change_admin = {
        "new_email": "admin.hacked@example.com",
        "password": "testpass123",
    }

    response = client.post(
        f"/api/users/{admin_id}/change-email",
        json=email_change_admin,
        headers=user_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Expected error: {response.json()['detail']}")

    # Step 7: Test role change (admin changes user role)
    print("\n7. Testing role change by admin...")
    role_change = {
        "new_role": "admin",
        "reason": "Test promotion for security testing",
    }

    response = client.post(
        f"/api/users/{user_id}/change-role",
        json=role_change,
        headers=admin_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Success: {response.json()['message']}")
    else:
        print(f"   Error: {response.json()}")

    # Step 8: Test user trying to change role (should fail)
    print("\n8. Testing user trying to change own role...")
    role_change_self = {"new_role": "admin", "reason": "Self promotion attempt"}

    response = client.post(
        f"/api/users/{user_id}/change-role",
        json=role_change_self,
        headers=user_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Expected error: {response.json()['detail']}")

    # Step 9: Verify user role was changed
    print("\n9. Verifying user role change...")
    response = client.get(f"/api/users/{user_id}", headers=admin_headers)
    if response.status_code == 200:
        user_data = response.json()
        print(f"   User role is now: {user_data['role']}")
        print(f"   User email is now: {user_data['email']}")


if __name__ == "__main__":
    test_security_endpoints()
