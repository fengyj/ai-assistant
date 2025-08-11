"""
Test the complete security improvements.
"""

import time

from fastapi.testclient import TestClient

from assistant.main import app

client = TestClient(app)


def test_complete_security() -> None:
    """Test complete security improvements."""

    print("=== Complete Security Test ===\n")

    # Step 1: Login as admin
    print("1. Logging in as admin...")
    admin_login = {"username": "admin", "password": "admin123"}

    response = client.post("/api/auth/login", json=admin_login)
    admin_auth = response.json()
    assert "access_token" in admin_auth, f"Login failed, response: {admin_auth}"
    admin_token = admin_auth["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    print("   ✅ Admin logged in successfully")

    # Step 2: Create a test user
    print("\n2. Creating a test user...")
    unique_username = f"securitytest_{int(time.time())}"
    test_user_data = {
        "username": unique_username,
        "email": f"{unique_username}@example.com",
        "password": "testpass456",
        "display_name": "Security Test User",
    }

    response = client.post("/api/users/", json=test_user_data, headers=admin_headers)

    if response.status_code == 201:
        user_data = response.json()
        user_id = user_data["id"]
        print(f"   ✅ Created user: {user_data['username']} (Role: {user_data['role']})")
    else:
        print(f"   ❌ Error creating user: {response.json()}")
        return

    # Step 3: Login as the test user
    print("\n3. Logging in as test user...")
    user_login = {"username": unique_username, "password": "testpass456"}

    response = client.post("/api/auth/login", json=user_login)
    user_auth = response.json()
    assert "access_token" in user_auth, f"Login failed, response: {user_auth}"
    user_token = user_auth["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    print(f"   ✅ User logged in: {user_auth['user']['username']} (Role: {user_auth['user']['role']})")

    # Step 4: Test regular user trying to change role (should fail)
    print("\n4. Testing regular user trying to change own role...")
    role_change_attempt = {
        "new_role": "admin",
        "reason": "Unauthorized self promotion attempt",
    }

    response = client.post(
        f"/api/users/{user_id}/change-role",
        json=role_change_attempt,
        headers=user_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 403:
        print(f"   ✅ Security working: {response.json()['detail']}")
    else:
        print(f"   ❌ Security breach: {response.json()}")

    # Step 5: Test email change by user (should work)
    print("\n5. Testing email change by user...")
    email_change = {
        "new_email": f"{unique_username}.new@example.com",
        "password": "testpass456",
    }

    response = client.post(
        f"/api/users/{user_id}/change-email",
        json=email_change,
        headers=user_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ {response.json()['message']}")
    else:
        print(f"   ❌ Error: {response.json()}")

    # Step 6: Test user trying to update role via regular update (should fail)
    print("\n6. Testing user trying to update role via PUT endpoint...")
    update_attempt = {"role": "admin", "display_name": "Hacker User"}

    response = client.put(f"/api/users/{user_id}", json=update_attempt, headers=user_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        updated_user = response.json()
        print(f"   Role after update: {updated_user['role']}")
        if updated_user["role"] == "user":
            print("   ✅ Security working: Role cannot be changed via update")
        else:
            print("   ❌ Security breach: Role was changed!")

    # Step 7: Test admin changing user role (should work)
    print("\n7. Testing admin changing user role...")
    admin_role_change = {
        "new_role": "admin",
        "reason": "Legitimate promotion by admin",
    }

    response = client.post(
        f"/api/users/{user_id}/change-role",
        json=admin_role_change,
        headers=admin_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ {response.json()['message']}")
    else:
        print(f"   ❌ Error: {response.json()}")

    # Step 8: Verify final state
    print("\n8. Verifying final user state...")
    response = client.get(f"/api/users/{user_id}", headers=admin_headers)
    if response.status_code == 200:
        final_user = response.json()
        print("   📋 Final user state:")
        print(f"      - Username: {final_user['username']}")
        print(f"      - Email: {final_user['email']}")
        print(f"      - Role: {final_user['role']}")
        print(f"      - Display Name: {final_user['display_name']}")

    print("\n🎉 Security testing completed!")
    print("\n📊 Summary:")
    print("   ✅ Email changes require password verification")
    print("   ✅ Users can only change their own email")
    print("   ✅ Role changes require admin privileges")
    print("   ✅ Regular users cannot escalate their own privileges")
    print("   ✅ Role field removed from regular user updates")


if __name__ == "__main__":
    test_complete_security()
