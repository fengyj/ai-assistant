// src/utils/apiHelpers.ts
import { useUserSession } from '../hooks/useUserSession';

/**
 * 自定义 hook，用于在组件中执行需要认证的 API 请求
 * 这个 hook 会自动处理 token 获取和刷新
 */
export const useAuthenticatedAPI = () => {
  const { 
    accessToken, 
    tokenType,
    sessionId, 
    refreshToken, 
    isAuthenticated,
    isTokenExpiringSoon 
  } = useUserSession();

  /**
   * 执行需要认证的 API 请求
   * @param apiCall 需要执行的 API 函数
   * @param params API 函数的参数
   */
  const executeAuthenticatedRequest = async <T, P extends unknown[]>(
    apiCall: (...args: P) => Promise<T>,
    ...params: P
  ): Promise<T> => {
    if (!isAuthenticated) {
      throw new Error('User is not authenticated');
    }

    // 检查 token 是否即将过期，主动刷新
    if (isTokenExpiringSoon() && sessionId) {
      console.log('Token expiring soon, refreshing proactively...');
      await refreshToken();
    }

    try {
      return await apiCall(...params);
    } catch (error: unknown) {
      // 如果是认证错误，尝试刷新 token
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { status?: number } };
        if (axiosError.response?.status === 401 && sessionId) {
          console.log('Received 401, attempting to refresh token...');
          const newToken = await refreshToken();
          
          if (newToken) {
            // 重试请求
            return await apiCall(...params);
          } else {
            throw new Error('Token refresh failed');
          }
        }
      }
      throw error;
    }
  };

  /**
   * 获取标准的 Authorization header 值
   */
  const getAuthHeader = (): string | null => {
    if (!accessToken || !tokenType) return null;
    return `${tokenType} ${accessToken}`;
  };

  return {
    executeAuthenticatedRequest,
    getAuthHeader,
    accessToken,
    tokenType,
    sessionId,
    isAuthenticated,
    isTokenExpiringSoon: isTokenExpiringSoon(),
  };
};

/**
 * 获取当前认证状态的工具函数
 * 可以在非组件环境中使用（比如工具函数、service 文件等）
 */
export const getAuthenticationInfo = () => {
  // 从 localStorage 直接获取，适用于非组件环境
  const accessToken = localStorage.getItem('access_token');
  const sessionId = localStorage.getItem('session_id');
  const userInfo = localStorage.getItem('user_info');
  
  return {
    accessToken,
    sessionId,
    user: userInfo ? JSON.parse(userInfo) : null,
    isAuthenticated: !!(sessionId && userInfo),
  };
};
