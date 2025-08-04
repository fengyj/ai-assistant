# OAuth Configuration Example

## Environment Variables for OAuth Setup

To enable OAuth authentication, set the following environment variables:

### Google OAuth
```bash
export GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

To get Google OAuth credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Set authorized redirect URIs: `http://localhost:8000/api/oauth/google/callback`

### Microsoft OAuth
```bash
export MICROSOFT_CLIENT_ID="your-microsoft-application-id"
export MICROSOFT_CLIENT_SECRET="your-microsoft-client-secret"
```

To get Microsoft OAuth credentials:
1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Set redirect URI: `http://localhost:8000/api/oauth/microsoft/callback`
5. Generate a client secret in "Certificates & secrets"

### Apple OAuth
```bash
export APPLE_CLIENT_ID="your-apple-service-id"
export APPLE_CLIENT_SECRET="your-apple-client-secret-jwt"
```

To get Apple OAuth credentials:
1. Go to [Apple Developer Portal](https://developer.apple.com/)
2. Navigate to "Certificates, Identifiers & Profiles"
3. Create a Services ID
4. Configure Sign in with Apple
5. Generate a client secret (JWT) using your private key

### Server Configuration
```bash
export BASE_URL="http://localhost:8000"  # For OAuth redirects
export HOST="localhost"
export PORT="8000"
export DEBUG="true"
```

### Production Considerations

For production deployment:

1. **Use HTTPS**: All OAuth providers require HTTPS in production
   ```bash
   export BASE_URL="https://your-domain.com"
   ```

2. **Secure Storage**: Store client secrets securely (environment variables, secret managers)

3. **Domain Verification**: Register your production domain with OAuth providers

4. **Rate Limiting**: Implement rate limiting for OAuth endpoints

5. **Logging**: Monitor OAuth flows for security

### Example .env file
```
# Server settings
HOST=localhost
PORT=8000
DEBUG=true
BASE_URL=http://localhost:8000

# Database
DATA_DIR=data

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Google OAuth
GOOGLE_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Microsoft OAuth
MICROSOFT_CLIENT_ID=12345678-1234-1234-1234-123456789abc
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

# Apple OAuth (optional)
# APPLE_CLIENT_ID=com.yourcompany.yourapp
# APPLE_CLIENT_SECRET=your-apple-jwt-client-secret
```

### Testing OAuth Flow

1. Start the server:
   ```bash
   python run_server.py
   ```

2. Get available providers:
   ```bash
   curl http://localhost:8000/api/oauth/providers
   ```

3. Get authorization URL:
   ```bash
   curl http://localhost:8000/api/oauth/google/authorize
   ```

4. Visit the authorization URL in browser and complete OAuth flow

5. The callback will be handled automatically by the server
