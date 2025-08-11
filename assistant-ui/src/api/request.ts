// src/api/request.ts
import axios from 'axios';
import type { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL } from "../config";
import { getAccessToken, refreshAccessToken, clearAuthData, isTokenNearExpiry } from '../utils/auth';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { "Content-Type": "application/json" }
});

// Track ongoing refresh request to prevent multiple concurrent refreshes
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: string) => void;
  reject: (reason: Error) => void;
}> = [];

// Process queued requests after token refresh
const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token!);
    }
  });
  
  failedQueue = [];
};

// Request interceptor to add auth token and handle token refresh
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Skip auth for auth-related endpoints
    const authEndpoints = ['/api/auth/login', '/api/auth/refresh', '/api/users/register'];
    const isAuthEndpoint = authEndpoints.some(endpoint => config.url?.includes(endpoint));
    
    if (!isAuthEndpoint) {
      const accessToken = getAccessToken();
      
      // If we have a token and it's near expiry, try to refresh it proactively
      if (accessToken && isTokenNearExpiry() && !isRefreshing) {
        console.log('Token is near expiry, refreshing proactively...');
        try {
          const newToken = await refreshAccessToken();
          if (newToken) {
            config.headers.Authorization = `Bearer ${newToken}`;
          }
        } catch (error) {
          console.warn('Proactive token refresh failed:', error);
          // Continue with existing token, let response interceptor handle it
          config.headers.Authorization = `Bearer ${accessToken}`;
        }
      } else if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token expiration
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Skip refresh for auth endpoints
      const authEndpoints = ['/api/auth/login', '/api/auth/refresh', '/api/users/register'];
      const isAuthEndpoint = authEndpoints.some(endpoint => originalRequest.url?.includes(endpoint));
      
      if (isAuthEndpoint) {
        return Promise.reject(error);
      }
      
      // If already refreshing, queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }
      
      isRefreshing = true;
      
      try {
        const newToken = await refreshAccessToken();
        
        if (newToken) {
          // Update the original request with new token
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          
          // Process any queued requests
          processQueue(null, newToken);
          
          // Retry the original request
          return api(originalRequest);
        } else {
          // Refresh failed, clear auth data and redirect to login
          processQueue(new Error('Token refresh failed'), null);
          
          // Redirect to login page
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
          
          return Promise.reject(error);
        }
      } catch (refreshError) {
        // Refresh failed, clear auth data
        const errorObj = refreshError instanceof Error ? refreshError : new Error('Token refresh failed');
        processQueue(errorObj, null);
        clearAuthData();
        
        // Redirect to login page
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    }
    
    // Handle other errors
    if (error.response?.status === 403) {
      console.error('Access forbidden:', error.response.data);
    } else if (error.response && error.response.status >= 500) {
      console.error('Server error:', error.response.data);
    }
    
    return Promise.reject(error);
  }
);

export default api;
