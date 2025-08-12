import React, { useState, useEffect, useCallback, useRef } from 'react';
import { UserSessionContext } from './UserSessionContext';
import { 
  getUserInfo, 
  clearAuthData, 
  getAccessToken, 
  getTokenType,
  getSessionId, 
  getTokenExpiryTime,
  refreshAccessToken,
  isTokenNearExpiry,
  type UserInfo 
} from '../utils/auth';
import type { UserSessionContextType } from './UserSessionContext';

export const UserSessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [tokenType, setTokenType] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [expiryTime, setExpiryTime] = useState<number | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  
  // 用于防止重复刷新
  const isRefreshing = useRef(false);
  const refreshTimer = useRef<NodeJS.Timeout | null>(null);

  // 从 localStorage 恢复认证状态
  const restoreAuthState = useCallback(() => {
    const userInfo = getUserInfo();
    const token = getAccessToken();
    const tokenTypeValue = getTokenType();
    const session = getSessionId();
    const expiry = getTokenExpiryTime();
    
    setUser(userInfo);
    setAccessToken(token);
    setTokenType(tokenTypeValue);
    setSessionId(session);
    setExpiryTime(expiry);
  }, []);

  // 检查 token 是否即将过期
  const isTokenExpiringSoon = useCallback((): boolean => {
    if (!expiryTime) return true;
    const now = Date.now();
    const fiveMinutes = 5 * 60 * 1000; // 5分钟
    return (expiryTime - now) < fiveMinutes;
  }, [expiryTime]);

  // 主动刷新 token
  const refreshToken = useCallback(async (): Promise<string | null> => {
    if (isRefreshing.current) {
      return null; // 防止重复刷新
    }

    isRefreshing.current = true;
    
    try {
      const newToken = await refreshAccessToken();
      if (newToken) {
        // 刷新成功，更新本地状态
        restoreAuthState();
      }
      return newToken;
    } finally {
      isRefreshing.current = false;
    }
  }, [restoreAuthState]);

  // 自动刷新逻辑
  const scheduleTokenRefresh = useCallback(() => {
    if (refreshTimer.current) {
      clearTimeout(refreshTimer.current);
    }

    if (!expiryTime || !sessionId) return;

    const now = Date.now();
    const timeUntilExpiry = expiryTime - now;
    const fiveMinutes = 5 * 60 * 1000;
    
    // 如果 token 将在 5 分钟内过期，立即刷新
    if (timeUntilExpiry < fiveMinutes) {
      refreshToken();
      return;
    }

    // 否则，安排在过期前 5 分钟刷新
    const timeUntilRefresh = timeUntilExpiry - fiveMinutes;
    refreshTimer.current = setTimeout(() => {
      refreshToken();
    }, timeUntilRefresh);
  }, [expiryTime, sessionId, refreshToken]);

  // 初始化时恢复认证状态
  useEffect(() => {
    const initializeAuth = async () => {
      setIsInitializing(true);
      
      // 首先从 localStorage 恢复状态
      restoreAuthState();
      
      // 如果有 sessionId 但 token 缺失或即将过期，尝试自动刷新
      const currentSessionId = getSessionId();
      const currentToken = getAccessToken();
      
      if (currentSessionId && (!currentToken || isTokenNearExpiry())) {
        console.log('Auto-refreshing token on initialization...');
        try {
          await refreshToken();
        } catch (error) {
          console.warn('Auto refresh failed during initialization:', error);
        }
      }
      
      setIsInitializing(false);
    };

    initializeAuth();
  }, [restoreAuthState, refreshToken]);

  // 监听过期时间变化，安排自动刷新
  useEffect(() => {
    scheduleTokenRefresh();
    
    return () => {
      if (refreshTimer.current) {
        clearTimeout(refreshTimer.current);
      }
    };
  }, [scheduleTokenRefresh]);

  // 监听 auth 变化事件
  useEffect(() => {
    const handleAuthChange = (event: CustomEvent) => {
      const userData = event.detail;
      setUser(userData);
      
      // 更新所有认证状态
      restoreAuthState();
    };

    window.addEventListener('authChanged', handleAuthChange as EventListener);
    
    return () => {
      window.removeEventListener('authChanged', handleAuthChange as EventListener);
    };
  }, [restoreAuthState]);

  const logout = useCallback(() => {
    if (refreshTimer.current) {
      clearTimeout(refreshTimer.current);
    }
    
    clearAuthData(); // 清除所有认证数据，包括 token
    setUser(null);
    setAccessToken(null);
    setTokenType(null);
    setSessionId(null);
    setExpiryTime(null);
    // 页面跳转逻辑由调用方处理
  }, []);

  const value: UserSessionContextType = {
    user,
    setUser,
    logout,
    isAuthenticated: !!user && !!sessionId,
    isInitializing,
    accessToken,
    tokenType,
    sessionId,
    expiryTime,
    refreshToken,
    isTokenExpiringSoon,
  };

  return (
    <UserSessionContext.Provider value={value}>
      {children}
    </UserSessionContext.Provider>
  );
};
