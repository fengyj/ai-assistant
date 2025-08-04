#!/usr/bin/env python3
"""
OAuth system demonstration and testing script.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from assistant.services.oauth_service import oauth_manager
from assistant.services.oauth_state_manager import OAuthStateManager
from assistant.core.config import config


async def demo_oauth_system():
    """Demonstrate the OAuth system capabilities."""

    print("=== OAuth System Demonstration ===\n")

    # 1. Show available providers
    print("1. Available OAuth Providers:")
    available_providers = oauth_manager.get_available_providers()
    print(f"   Configured providers: {available_providers}")

    if not available_providers:
        print("   No OAuth providers configured!")
        print("   Please set environment variables for OAuth credentials.")
        print("   See OAUTH_SETUP.md for details.")
        return

    # 2. Generate authorization URLs
    print("\n2. Authorization URLs:")
    for provider in available_providers:
        try:
            auth_url, state_token = oauth_manager.generate_authorization_url(
                provider, {"demo": True}
            )
            print(f"   {provider.title()}:")
            print(f"     State: {state_token}")
            print(f"     URL: {auth_url[:100]}...")
        except Exception as e:
            print(f"   {provider.title()}: Error - {e}")

    # 3. Show state management
    print("\n3. OAuth State Management:")
    state_manager = OAuthStateManager()

    # Create some test states
    test_states = []
    for provider in available_providers[:2]:  # Test first 2 providers
        state_token = state_manager.create_state(
            provider=provider,
            redirect_uri=f"http://localhost:8000/api/oauth/{provider}/callback",
            metadata={"test": True, "demo_id": len(test_states)},
        )
        test_states.append((provider, state_token))
        print(f"   Created state for {provider}: {state_token[:20]}...")

    # Validate states
    print("\n4. State Validation:")
    for provider, state_token in test_states:
        oauth_state = state_manager.validate_and_consume_state(state_token, provider)
        if oauth_state:
            print(f"   ✓ {provider}: Valid state (consumed)")
        else:
            print(f"   ✗ {provider}: Invalid state")

    # Try to validate again (should fail as they're consumed)
    print("\n5. State Consumption Test:")
    for provider, state_token in test_states:
        oauth_state = state_manager.validate_and_consume_state(state_token, provider)
        if oauth_state:
            print(f"   ✗ {provider}: State reused (security issue!)")
        else:
            print(f"   ✓ {provider}: State properly consumed")

    # 6. Provider-specific features
    print("\n6. Provider-Specific Features:")
    for provider_name in available_providers:
        provider = oauth_manager.get_provider(provider_name)
        print(f"   {provider_name.title()}:")
        print(f"     Provider class: {provider.__class__.__name__}")
        print(f"     Authorization URL: {provider.config.authorization_url}")
        print(f"     Token URL: {provider.config.token_url}")
        print(f"     Scopes: {', '.join(provider.config.scope)}")

    # 7. Configuration info
    print("\n7. Configuration:")
    print(f"   Host: {config.host}:{config.port}")
    print(f"   Base URL: {getattr(config, 'base_url', 'Not set')}")
    print(f"   Data directory: {config.data_dir}")
    print(f"   Debug mode: {config.debug}")

    # 8. Security features
    print("\n8. Security Features:")
    print("   ✓ State tokens for CSRF protection")
    print("   ✓ State expiration (10 minutes)")
    print("   ✓ State consumption (one-time use)")
    print("   ✓ Provider validation")
    print("   ✓ Secure HTTP client (httpx)")
    print("   ✓ Configurable redirect URIs")

    print("\n=== OAuth System Ready ===")
    print("\nTo test with real OAuth:")
    print("1. Configure OAuth credentials (see OAUTH_SETUP.md)")
    print("2. Start the server: python run_server.py")
    print("3. Visit: http://localhost:8000/api/oauth/providers")
    print("4. Get auth URL: http://localhost:8000/api/oauth/google/authorize")
    print("5. Complete OAuth flow in browser")


def show_config_help():
    """Show configuration help."""
    print("OAuth Configuration Help")
    print("=" * 50)
    print()
    print("To enable OAuth providers, set these environment variables:")
    print()
    print("Google OAuth:")
    print("  export GOOGLE_CLIENT_ID='your-client-id'")
    print("  export GOOGLE_CLIENT_SECRET='your-client-secret'")
    print()
    print("Microsoft OAuth:")
    print("  export MICROSOFT_CLIENT_ID='your-client-id'")
    print("  export MICROSOFT_CLIENT_SECRET='your-client-secret'")
    print()
    print("Apple OAuth:")
    print("  export APPLE_CLIENT_ID='your-service-id'")
    print("  export APPLE_CLIENT_SECRET='your-jwt-secret'")
    print()
    print("See OAUTH_SETUP.md for detailed setup instructions.")


async def test_oauth_flow():
    """Test OAuth flow simulation."""
    print("=== OAuth Flow Test ===\n")

    available_providers = oauth_manager.get_available_providers()
    if not available_providers:
        print("No OAuth providers configured for testing.")
        return

    provider_name = available_providers[0]
    print(f"Testing OAuth flow with {provider_name.title()}")

    try:
        # Step 1: Generate authorization URL
        auth_url, state_token = oauth_manager.generate_authorization_url(
            provider_name, {"test_flow": True}
        )
        print(f"1. Authorization URL generated")
        print(f"   State: {state_token}")
        print(f"   URL: {auth_url}")

        # Step 2: Simulate callback (this would normally come from OAuth provider)
        print(f"\n2. Simulating OAuth callback...")

        # In a real scenario, the OAuth provider would redirect to our callback
        # with a code and the state token. We'll simulate an error here since
        # we don't have real OAuth credentials.
        print(
            "   Note: Real OAuth flow requires valid credentials and user interaction"
        )
        print("   This demo shows the URL generation and state management only")

        # Step 3: State cleanup
        cleanup_count = await oauth_manager.cleanup_expired_states()
        print(f"\n3. Cleaned up {cleanup_count} expired states")

    except Exception as e:
        print(f"Error during OAuth flow test: {e}")


async def main():
    """Main demo function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "config":
            show_config_help()
            return
        elif sys.argv[1] == "test":
            await test_oauth_flow()
            return

    await demo_oauth_system()


if __name__ == "__main__":
    print("OAuth System Demo")
    print("Usage:")
    print("  python demo_oauth.py        # Show system overview")
    print("  python demo_oauth.py config # Show configuration help")
    print("  python demo_oauth.py test   # Test OAuth flow")
    print()

    asyncio.run(main())
