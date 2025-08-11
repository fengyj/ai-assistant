// Enhanced authentication utilities with JWT + Session support

export interface UserInfo {
  id: string;
  username: string;
  display_name?: string;
  role: string;
  status: string;
  email?: string;
  permissions?: string[];
}

export interface AuthTokens {
  access_token: string;
  session_id: string;
  expires_in: number;
  user: UserInfo;
}

// Token management
export const getAccessToken = () => localStorage.getItem("access_token");
export const getSessionId = () => localStorage.getItem("session_id");
export const getUserInfo = (): UserInfo | null => {
  const userStr = localStorage.getItem("user_info");
  return userStr ? JSON.parse(userStr) : null;
};

export const setAuthData = (tokens: AuthTokens) => {
  localStorage.setItem("access_token", tokens.access_token);
  localStorage.setItem("session_id", tokens.session_id);
  localStorage.setItem("user_info", JSON.stringify(tokens.user));
  localStorage.setItem("token_expires_at", (Date.now() + tokens.expires_in * 1000).toString());
  
  // 触发自定义事件，用于通知其他组件token变化
  window.dispatchEvent(new CustomEvent('authChanged', { detail: tokens.user }));
};

export const clearAuthData = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("session_id");
  localStorage.removeItem("user_info");
  localStorage.removeItem("token_expires_at");
  
  // 触发自定义事件，用于通知其他组件token变化
  window.dispatchEvent(new CustomEvent('authChanged', { detail: null }));
};

// 检查access token是否即将过期（5分钟内）
export const isTokenNearExpiry = (): boolean => {
  const expiresAt = localStorage.getItem("token_expires_at");
  if (!expiresAt) return true;
  
  const expiryTime = parseInt(expiresAt);
  const now = Date.now();
  const fiveMinutes = 5 * 60 * 1000; // 5分钟
  
  return (expiryTime - now) < fiveMinutes;
};

// 检查用户是否已认证（有有效的session）
export const isAuthenticated = (): boolean => {
  const accessToken = getAccessToken();
  const sessionId = getSessionId();
  
  // 如果没有session_id，说明没有长期认证
  if (!sessionId) return false;
  
  // 如果有session但没有access token，需要刷新
  if (!accessToken) return true; // 这里返回true，让拦截器去刷新token
  
  // 如果access token即将过期，仍然认为已认证，让拦截器处理刷新
  return true;
};

// 从JWT中解析用户信息（备用方法）
export const parseTokenUserInfo = (token: string): Partial<UserInfo> | null => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return {
      id: payload.sub,
      username: payload.username,
      display_name: payload.display_name,
      role: payload.role,
      status: payload.status,
      email: payload.email,
      permissions: payload.permissions
    };
  } catch (error) {
    console.warn('Failed to parse user info from token:', error);
    return null;
  }
};

// 登出功能
export const logout = async (): Promise<void> => {
  const accessToken = getAccessToken();
  
  // 如果有access token，尝试调用后端登出API
  if (accessToken) {
    try {
      // 动态导入API实例以避免循环依赖
      const { logout: logoutAPI } = await import('../api/auth');
      await logoutAPI();
      return; // API调用成功，已在auth.ts中处理了清理和跳转
    } catch (error) {
      console.warn('Logout API call failed:', error);
      // 继续本地清理
    }
  }
  
  clearAuthData();
};

// 刷新access token
export const refreshAccessToken = async (): Promise<string | null> => {
  const sessionId = getSessionId();
  
  if (!sessionId) {
    clearAuthData();
    return null;
  }
  
  try {
    // 动态导入API实例以避免循环依赖
    const { default: api } = await import('../api/request');
    
    const response = await api.post('/api/auth/refresh', {
      session_id: sessionId,
      extend_session: true
    });
    
    const newAccessToken = response.data.access_token;
    const expiresIn = response.data.expires_in || 900; // 默认15分钟
    
    localStorage.setItem("access_token", newAccessToken);
    localStorage.setItem("token_expires_at", (Date.now() + expiresIn * 1000).toString());
    
    return newAccessToken;
    
  } catch (error) {
    console.error('Token refresh failed:', error);
    clearAuthData();
    return null;
  }
};

// Legacy support - 保持向后兼容
export const getToken = getAccessToken;
export const setToken = (token: string) => {
  localStorage.setItem("access_token", token);
  window.dispatchEvent(new CustomEvent('tokenChanged'));
};
export const removeToken = clearAuthData;
