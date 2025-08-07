"""
Simple test script to validate the user API with authentication.
"""

import httpx
import pytest

BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio  # type: ignore[misc]
async def test_user_api() -> None:
    """Test user API endpoints with authentication."""

    async with httpx.AsyncClient() as client:
        print("=== User API Authentication Test ===\n")

        # Test 1: Try accessing protected endpoint without token (should fail)
        print("1. Testing access without authentication...")
        try:
            response = await client.get(f"{BASE_URL}/api/users/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")

        # Test 2: Login with default admin user
        print("\n2. Testing login with admin user...")
        login_data = {"username": "admin", "password": "admin123"}

        try:
            response = await client.post(f"{BASE_URL}/api/users/login", json=login_data)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                auth_data = response.json()
                access_token = auth_data["access_token"]
                user_info = auth_data["user"]
                print(f"   Token obtained: {access_token[:20]}...")
                print(f"   User: {user_info['username']} ({user_info['role']})")

                # Test 3: Access protected endpoint with token
                print("\n3. Testing access with authentication...")
                headers = {"Authorization": f"Bearer {access_token}"}

                response = await client.get(f"{BASE_URL}/api/users/", headers=headers)
                print(f"   Status: {response.status_code}")

                if response.status_code == 200:
                    users = response.json()
                    print(f"   Found {len(users)} users")
                    for user in users:
                        print(f"     - {user['username']} ({user['role']})")
                else:
                    print(f"   Error: {response.json()}")

                # Test 4: Try to access specific user data
                print("\n4. Testing user-specific data access...")
                admin_id = user_info["id"]
                response = await client.get(f"{BASE_URL}/api/users/{admin_id}", headers=headers)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"   User data: {user_data['username']}")
                else:
                    print(f"   Error: {response.json()}")

                # Test 5: Try to create a new user (admin only)
                print("\n5. Testing user creation (admin only)...")
                new_user_data = {
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "testpass123",
                    "display_name": "Test User",
                    "role": "user",
                }

                response = await client.post(f"{BASE_URL}/api/users/", json=new_user_data, headers=headers)
                print(f"   Status: {response.status_code}")
                if response.status_code == 201:
                    created_user = response.json()
                    print(f"   Created user: {created_user['username']}")
                else:
                    print(f"   Error: {response.json()}")

            else:
                print(f"   Login failed: {response.json()}")

        except Exception as e:
            print(f"   Error: {e}")


if __name__ == "__main__":
    import asyncio

    print("Testing User API with Authentication")
    print("Make sure the server is running: python run_server.py")
    print()
    asyncio.run(test_user_api())
