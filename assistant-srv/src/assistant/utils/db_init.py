"""
Database initialization and migration script.
"""

import os
import json
from datetime import datetime, timezone
from ..core import config
from ..models import User, UserRole, UserStatus, UserProfile
from ..utils.security import PasswordHasher


def ensure_data_directory() -> None:
    """Ensure data directory exists."""
    os.makedirs(config.data_dir, exist_ok=True)
    print(f"Data directory ensured: {config.data_dir}")


def create_default_admin_user() -> None:
    """Create default admin user if no users exist."""
    users_file = os.path.join(config.data_dir, config.users_file)

    if os.path.exists(users_file):
        with open(users_file, "r", encoding="utf-8") as f:
            try:
                users_data = json.load(f)
                if users_data:  # Users already exist
                    print("Users already exist, skipping default admin creation")
                    return
            except json.JSONDecodeError:
                pass  # File is corrupted, proceed to create admin

    # Create default admin user
    password_hasher = PasswordHasher()
    admin_user = User(
        username="admin",
        email="admin@localhost",
        password_hash=password_hasher.hash_password("admin123"),
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        profile=UserProfile(display_name="System Administrator", language="en"),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # Save to file
    users_data = [admin_user.to_dict()]
    with open(users_file, "w", encoding="utf-8") as f:
        json.dump(users_data, f, indent=2, ensure_ascii=False)

    print(f"Default admin user created: admin/admin123")


def initialize_database() -> None:
    """Initialize database and create default data."""
    print("Initializing database...")

    ensure_data_directory()
    create_default_admin_user()

    print("Database initialization completed!")


if __name__ == "__main__":
    initialize_database()
