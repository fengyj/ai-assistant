"""
Test new security endpoints for email and role changes.
"""

from fastapi.testclient import TestClient

from assistant.main import app

client = TestClient(app)


def test_security_endpoints() -> None:
    """Test email change and role change endpoints."""

    print("=== Security Endpoints Test ===\n")

    # Step 1: Login as admin
    print("1. Logging in as admin...")
    admin_login = {"username": "admin", "password": "admin123"}

    response = client.post("/api/users/login", json=admin_login)
    admin_auth = response.json()
    admin_token = admin_auth["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    admin_id = admin_auth["user"]["id"]

    print("   Admin logged in successfully")

    # Step 2: Try to get or create a test user
    print("\n2. Setting up test user...")

    # First, try to get existing users to see what's available
    users_response = client.get("/api/users/", headers=admin_headers)
    if users_response.status_code == 200:
        users = users_response.json()
        test_user = None

        # Look for an existing non-admin user
        for user in users:
            if user["role"] == "user":
                test_user = user
                break

        if test_user:
            print(f"   Using existing user: {test_user['username']}")
            user_id = test_user["id"]
            # Try to login with a common password or reset password
            user_login = {"username": test_user["username"], "password": "password123"}
            response = client.post("/api/users/login", json=user_login)

            if response.status_code != 200:
                # If login fails, let's reset the password as admin
                print("   Login failed, resetting password...")
                password_reset = {"user_id": user_id, "new_password": "password123"}
                # Note: This endpoint might not exist, so we'll handle the error
                reset_response = client.post("/api/users/reset-password", json=password_reset, headers=admin_headers)
                if reset_response.status_code == 200:
                    response = client.post("/api/users/login", json=user_login)
                else:
                    print("   Password reset failed, creating new user...")
                    # Create a new test user with unique name
                    import time

                    unique_username = f"testuser_{int(time.time())}"
                    test_user_data = {
                        "username": unique_username,
                        "email": f"{unique_username}@example.com",
                        "password": "password123",
                        "display_name": "Test User",
                    }

                    create_response = client.post("/api/users/", json=test_user_data, headers=admin_headers)
                    if create_response.status_code == 201:
                        print(f"   Created new user: {unique_username}")
                        user_login = {"username": unique_username, "password": "password123"}
                        response = client.post("/api/users/login", json=user_login)
                    else:
                        print(f"   Failed to create user: {create_response.json()}")
                        return
        else:
            print("   No regular users found, creating new one...")
            # Create a new test user
            import time

            unique_username = f"testuser_{int(time.time())}"
            test_user_data = {
                "username": unique_username,
                "email": f"{unique_username}@example.com",
                "password": "password123",
                "display_name": "Test User",
            }

            create_response = client.post("/api/users/", json=test_user_data, headers=admin_headers)
            if create_response.status_code == 201:
                print(f"   Created new user: {unique_username}")
                user_login = {"username": unique_username, "password": "password123"}
                response = client.post("/api/users/login", json=user_login)
            else:
                print(f"   Failed to create user: {create_response.json()}")
                return
    else:
        print(f"   Failed to get users list: {users_response.json()}")
        return

    if response.status_code != 200:
        print(f"   Login still failed: {response.json()}")
        return

    user_auth = response.json()
    user_token = user_auth["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    user_id = user_auth["user"]["id"]

    print(f"   User logged in: {user_auth['user']['username']}")

    # Step 3: Test email change (user tries to change own email)
    print("\n3. Testing email change...")
    email_change = {
        "new_email": "testuser.new@example.com",
        "password": "password123",
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

    # Step 4: Test email change with wrong password
    print("\n4. Testing email change with wrong password...")
    email_change_wrong = {
        "new_email": "testuser.wrong@example.com",
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

    # Step 5: Test user trying to change admin's email (should fail)
    print("\n5. Testing user trying to change admin's email...")
    email_change_admin = {
        "new_email": "admin.hacked@example.com",
        "password": "password123",
    }

    response = client.post(
        f"/api/users/{admin_id}/change-email",
        json=email_change_admin,
        headers=user_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Expected error: {response.json()['detail']}")

    # Step 6: Test role change (admin changes user role)
    print("\n6. Testing role change by admin...")
    role_change = {"new_role": "admin", "reason": "Test promotion"}

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

    # Step 7: Test user trying to change role (should fail)
    print("\n7. Testing user trying to change own role...")
    role_change_self = {"new_role": "admin", "reason": "Self promotion"}

    response = client.post(
        f"/api/users/{user_id}/change-role",
        json=role_change_self,
        headers=user_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Expected error: {response.json()['detail']}")

    # Step 8: Verify user role was changed
    print("\n8. Verifying user role change...")
    response = client.get(f"/api/users/{user_id}", headers=admin_headers)
    if response.status_code == 200:
        user_data = response.json()
        print(f"   User role is now: {user_data['role']}")


if __name__ == "__main__":
    test_security_endpoints()
