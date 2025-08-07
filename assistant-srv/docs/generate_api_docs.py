"""
Generate API documentation for user management.
"""

import json
import os
import sys
from typing import Any, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.openapi.utils import get_openapi  # noqa: E402

from assistant.main import app  # noqa: E402


def generate_api_docs() -> Dict[str, Any]:
    """Generate OpenAPI documentation."""

    openapi_schema = get_openapi(
        title="Personal AI Assistant Server API",
        version="0.1.0",
        description="""
        ## User Management APIs

        The assistant supports multi-users with the following core features:

        ### Core Features

        - User registration and authentication
        - User profile management
        - Multi-user session handling
        - OAuth support (Google, Microsoft, Apple)

        ### Available Endpoints

        #### User Management
        - `POST /api/users/` - Create new user
        - `GET /api/users/{user_id}` - Get user by ID
        - `GET /api/users/` - Get all users
        - `PUT /api/users/{user_id}` - Update user
        - `DELETE /api/users/{user_id}` - Delete user
        - `POST /api/users/login` - User login
        - `POST /api/users/{user_id}/change-password` - Change password
        - `GET /api/users/search/{query}` - Search users

        #### OAuth Authentication
        - `GET /api/oauth/{provider}/authorize` - Get OAuth authorization URL
        - `POST /api/oauth/{provider}/callback` - Handle OAuth callback
        - `POST /api/oauth/{provider}/unlink/{user_id}` - Unlink OAuth provider

        #### Session Management
        - `POST /api/sessions/` - Create session
        - `GET /api/sessions/{token}` - Get session by token
        - `GET /api/sessions/user/{user_id}` - Get user sessions
        - `POST /api/sessions/{token}/refresh` - Refresh session
        - `DELETE /api/sessions/{token}` - Terminate session
        - `DELETE /api/sessions/user/{user_id}/all` - Terminate all user sessions
        - `POST /api/sessions/cleanup` - Clean up expired sessions
        - `POST /api/sessions/{token}/validate` - Validate session
        """,
        routes=app.routes,
    )

    return openapi_schema


def save_api_docs() -> None:
    """Save API documentation to file."""
    docs = generate_api_docs()

    # Save as JSON
    with open("api_docs.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

    print("API documentation saved to api_docs.json")

    # Print summary
    print("\n=== API ENDPOINTS SUMMARY ===\n")

    endpoints = []
    for path, methods in docs["paths"].items():
        for method, details in methods.items():
            endpoint = f"{method.upper()} {path}"
            summary = details.get("summary", "No summary")
            endpoints.append(f"  {endpoint:<50} - {summary}")

    for endpoint in sorted(endpoints):
        print(endpoint)

    print(f"\nTotal endpoints: {len(endpoints)}")


if __name__ == "__main__":
    save_api_docs()
