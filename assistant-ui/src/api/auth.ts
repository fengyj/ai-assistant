// Authentication API functions
import api from './request';
import { getAccessToken, getSessionId, clearAuthData } from '../utils/auth';

export interface RefreshTokenRequest {
  session_id: string;
  extend_session?: boolean;
}

export interface RefreshTokenResponse {
  access_token: string;
  expires_in: number;
}

export interface ValidateTokenResponse {
  valid: boolean;
  user?: {
    id: string;
    username: string;
    display_name?: string;
    role: string;
    status: string;
    email?: string;
    permissions?: string[];
  };
}

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

// Validate current access token
export const validateToken = async (): Promise<ValidateTokenResponse> => {
  const response = await api.get<ValidateTokenResponse>('/api/auth/validate');
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
  refreshToken,
  validateToken,
  logout
};
