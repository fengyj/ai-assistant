"""
Test OAuth permission handling.
"""

import time

from fastapi.testclient import TestClient

from assistant.main import app

client = TestClient(app)


def test_oauth_permissions() -> None:
    """Test OAuth login and permissions."""

    print("=== OAuth Permission Test ===\n")

    # Step 1: Login as admin first to see existing users
    print("1. Logging in as admin...")
    admin_login = {"username": "admin", "password": "admin123"}

    response = client.post("/api/users/login", json=admin_login)
    admin_auth = response.json()
    admin_token = admin_auth["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    print("   Admin logged in successfully")

    # Step 2: Get all users to see current state
    print("\n2. Getting all users...")
    response = client.get("/api/users/", headers=admin_headers)
    users = response.json()
    print(f"   Current users: {len(users)}")
    for user in users:
        print(f"   - {user['username']} ({user['role']})")

    # Step 3: Simulate OAuth login for new user
    print("\n3. Simulating OAuth login for new user...")
    unique_id = str(int(time.time()))
    oauth_user_data = {
        "provider": "google",
        "provider_id": f"google_{unique_id}",
        "email": f"oauth.user.{unique_id}@gmail.com",
        "username": f"oauth_user_{unique_id}",
        "display_name": "OAuth Test User",
        "avatar": "https://lh3.googleusercontent.com/a/test-avatar",
    }

    response = client.post("/api/users/oauth-login", json=oauth_user_data)

    if response.status_code == 200:
        oauth_auth = response.json()
        oauth_token = oauth_auth["access_token"]
        oauth_headers = {"Authorization": f"Bearer {oauth_token}"}

        print(f"   OAuth user logged in: {oauth_auth['user']['username']}")
        print(f"   User role: {oauth_auth['user']['role']}")

        # Step 4: Test OAuth user permissions
        print("\n4. Testing OAuth user permissions...")

        # Should not be able to get all users (default role is 'user')
        print("   - Trying to get all users (should fail)...")
        response = client.get("/api/users/", headers=oauth_headers)
        print(f"     Status: {response.status_code}")
        if response.status_code != 200:
            print(f"     Error: {response.json()['detail']}")

        # Should be able to get own data
        user_id = oauth_auth["user"]["id"]
        print("   - Trying to get own user data (should succeed)...")
        response = client.get(f"/api/users/{user_id}", headers=oauth_headers)
        print(f"     Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"     Success: Got data for {user_data['username']}")

        # Step 5: Admin upgrades OAuth user to admin
        print("\n5. Admin upgrading OAuth user to admin role...")
        update_data = {"role": "admin"}
        response = client.put(
            f"/api/users/{user_id}",
            json=update_data,
            headers=admin_headers,
        )

        if response.status_code == 200:
            print("   OAuth user upgraded to admin")

            # Step 6: Test new admin permissions
            print("\n6. Re-login OAuth user and test admin permissions...")

            # Re-login to get new token with updated role
            response = client.post("/api/users/oauth-login", json=oauth_user_data)

            new_oauth_auth = response.json()
            new_oauth_token = new_oauth_auth["access_token"]
            new_oauth_headers = {"Authorization": f"Bearer {new_oauth_token}"}

            print(f"   New role: {new_oauth_auth['user']['role']}")

            # Now should be able to get all users
            print("   - Trying to get all users (should succeed now)...")
            response = client.get("/api/users/", headers=new_oauth_headers)
            print(f"     Status: {response.status_code}")
            if response.status_code == 200:
                all_users = response.json()
                print(f"     Success: Retrieved {len(all_users)} users")

    else:
        print(f"   OAuth login failed: {response.json()}")


if __name__ == "__main__":
    test_oauth_permissions()
