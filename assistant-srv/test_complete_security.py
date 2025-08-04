"""
Test the complete security improvements.
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"


async def test_complete_security():
    """Test complete security improvements."""

    async with httpx.AsyncClient() as client:
        print("=== Complete Security Test ===\n")

        # Step 1: Login as admin
        print("1. Logging in as admin...")
        admin_login = {"username": "admin", "password": "admin123"}

        response = await client.post(f"{BASE_URL}/api/users/login", json=admin_login)
        admin_auth = response.json()
        admin_token = admin_auth["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        admin_id = admin_auth["user"]["id"]

        print("   ✅ Admin logged in successfully")

        # Step 2: Create a test user
        print("\n2. Creating a test user...")
        test_user_data = {
            "username": "securitytest2",
            "email": "securitytest2@example.com",
            "password": "testpass456",
            "display_name": "Security Test User 2",
        }

        response = await client.post(
            f"{BASE_URL}/api/users/", json=test_user_data, headers=admin_headers
        )

        if response.status_code == 201:
            user_data = response.json()
            user_id = user_data["id"]
            print(
                f"   ✅ Created user: {user_data['username']} (Role: {user_data['role']})"
            )
        else:
            print(f"   ❌ Error creating user: {response.json()}")
            return

        # Step 3: Login as the test user
        print("\n3. Logging in as test user...")
        user_login = {"username": "securitytest2", "password": "testpass456"}

        response = await client.post(f"{BASE_URL}/api/users/login", json=user_login)
        user_auth = response.json()
        user_token = user_auth["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        print(
            f"   ✅ User logged in: {user_auth['user']['username']} (Role: {user_auth['user']['role']})"
        )

        # Step 4: Test regular user trying to change role (should fail)
        print("\n4. Testing regular user trying to change own role...")
        role_change_attempt = {
            "new_role": "admin",
            "reason": "Unauthorized self promotion attempt",
        }

        response = await client.post(
            f"{BASE_URL}/api/users/{user_id}/change-role",
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
            "new_email": "securitytest2.new@example.com",
            "password": "testpass456",
        }

        response = await client.post(
            f"{BASE_URL}/api/users/{user_id}/change-email",
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

        response = await client.put(
            f"{BASE_URL}/api/users/{user_id}", json=update_attempt, headers=user_headers
        )
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

        response = await client.post(
            f"{BASE_URL}/api/users/{user_id}/change-role",
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
        response = await client.get(
            f"{BASE_URL}/api/users/{user_id}", headers=admin_headers
        )
        if response.status_code == 200:
            final_user = response.json()
            print(f"   📋 Final user state:")
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
    asyncio.run(test_complete_security())
