// Authentication API functions
import api from './request';
import { getAccessToken, getSessionId, clearAuthData, setAuthData, type AuthTokens } from '../utils/auth';

// Login request/response interfaces
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  session_id: string;
  expires_in: number;
  user: {
    id: string;
    username: string;
    display_name?: string;
    role: string;
    status: string;
    email?: string;
    permissions?: string[];
  };
}

// Refresh token interfaces
export interface RefreshTokenRequest {
  session_id: string;
  extend_session?: boolean;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

// Login function
export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>('/api/auth/login', {
    username: credentials.username.trim(),
    password: credentials.password
  });

  const { access_token, token_type, session_id, expires_in, user } = response.data;

  // Validate response data
  if (!access_token || !session_id || !user) {
    throw new Error('登录响应数据不完整');
  }

  // Store authentication data
  const authTokens: AuthTokens = {
    access_token,
    token_type: token_type || 'Bearer',
    session_id,
    expires_in: expires_in || 900, // Default to 15 minutes
    user
  };

  setAuthData(authTokens);
  
  return response.data;
};

// Refresh access token using session ID
export const refreshToken = async (extend_session = true): Promise<RefreshTokenResponse> => {
  const sessionId = getSessionId();
  
  if (!sessionId) {
    throw new Error('No session ID available');
  }
  
  const response = await api.post<RefreshTokenResponse>('/api/auth/refresh', {
    session_id: sessionId,
    extend_session
  });
  
  return response.data;
};

// Logout and invalidate session
export const logout = async (): Promise<void> => {
  const accessToken = getAccessToken();
  
  if (accessToken) {
    try {
      await api.post('/api/auth/logout');
    } catch (error) {
      console.warn('Logout API call failed:', error);
      // Continue with local cleanup even if API call fails
    }
  }
  
  // Always clear local auth data
  clearAuthData();
  
  // Redirect to login page
  if (window.location.pathname !== '/login') {
    window.location.href = '/login';
  }
};

export default {
  login,
  refreshToken,
  logout
};
