"""
Test user permissions with non-admin user.
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"


async def test_user_permissions():
    """Test user permissions with different roles."""

    async with httpx.AsyncClient() as client:
        print("=== User Permission Test ===\n")

        # Step 1: Login as admin to create a regular user
        print("1. Logging in as admin...")
        admin_login = {"username": "admin", "password": "admin123"}

        response = await client.post(f"{BASE_URL}/api/users/login", json=admin_login)
        admin_auth = response.json()
        admin_token = admin_auth["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Step 2: Create a regular user
        print("2. Creating a regular user...")
        regular_user_data = {
            "username": "regularuser",
            "email": "regular@example.com",
            "password": "userpass123",
            "display_name": "Regular User",
            "role": "user",
        }

        response = await client.post(
            f"{BASE_URL}/api/users/", json=regular_user_data, headers=admin_headers
        )

        if response.status_code == 201:
            new_user = response.json()
            user_id = new_user["id"]
            print(f"   Created user: {new_user['username']} (ID: {user_id})")
        else:
            print(f"   Failed to create user: {response.json()}")
            return

        # Step 3: Login as regular user
        print("\n3. Logging in as regular user...")
        user_login = {"username": "regularuser", "password": "userpass123"}

        response = await client.post(f"{BASE_URL}/api/users/login", json=user_login)
        user_auth = response.json()
        user_token = user_auth["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        print(f"   User logged in: {user_auth['user']['username']}")

        # Step 4: Test what regular user can access
        print("\n4. Testing regular user permissions...")

        # Try to get all users (should fail - admin only)
        print("   - Trying to get all users (should fail)...")
        response = await client.get(f"{BASE_URL}/api/users/", headers=user_headers)
        print(f"     Status: {response.status_code}")
        if response.status_code != 200:
            print(f"     Error: {response.json()['detail']}")

        # Try to get own user data (should succeed)
        print("   - Trying to get own user data (should succeed)...")
        response = await client.get(
            f"{BASE_URL}/api/users/{user_id}", headers=user_headers
        )
        print(f"     Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"     Success: Got data for {user_data['username']}")

        # Try to get admin user data (should fail)
        admin_id = admin_auth["user"]["id"]
        print("   - Trying to get admin user data (should fail)...")
        response = await client.get(
            f"{BASE_URL}/api/users/{admin_id}", headers=user_headers
        )
        print(f"     Status: {response.status_code}")
        if response.status_code != 200:
            print(f"     Error: {response.json()['detail']}")

        # Try to create another user (should fail - admin only)
        print("   - Trying to create another user (should fail)...")
        another_user = {
            "username": "anotheruser",
            "email": "another@example.com",
            "password": "pass123",
            "role": "user",
        }
        response = await client.post(
            f"{BASE_URL}/api/users/", json=another_user, headers=user_headers
        )
        print(f"     Status: {response.status_code}")
        if response.status_code != 201:
            print(f"     Error: {response.json()['detail']}")

        # Try to change own password (should succeed)
        print("   - Trying to change own password (should succeed)...")
        password_change = {"old_password": "userpass123", "new_password": "newpass123"}
        response = await client.post(
            f"{BASE_URL}/api/users/{user_id}/change-password",
            json=password_change,
            headers=user_headers,
        )
        print(f"     Status: {response.status_code}")
        if response.status_code == 200:
            print(f"     Success: {response.json()['message']}")

        # Try to delete a user (should fail - admin only)
        print("   - Trying to delete a user (should fail)...")
        response = await client.delete(
            f"{BASE_URL}/api/users/{user_id}", headers=user_headers
        )
        print(f"     Status: {response.status_code}")
        if response.status_code != 204:
            print(f"     Error: {response.json()['detail']}")


if __name__ == "__main__":
    asyncio.run(test_user_permissions())
