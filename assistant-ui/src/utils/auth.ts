// Utility functions for authentication
export const getToken = () => localStorage.getItem("token");

export const setToken = (token: string) => {
  localStorage.setItem("token", token);
  // 触发自定义事件，用于通知其他组件token变化
  window.dispatchEvent(new CustomEvent('tokenChanged'));
};

export const removeToken = () => {
  localStorage.removeItem("token");
  // 触发自定义事件，用于通知其他组件token变化
  window.dispatchEvent(new CustomEvent('tokenChanged'));
};

export const isAuthenticated = () => {
  const token = getToken();
  if (!token) return false;
  
  try {
    // 检查token是否过期（简单的JWT解析）
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp > currentTime;
  } catch (error) {
    // 如果token格式不正确，则认为未认证
    console.warn('Invalid token format:', error);
    removeToken();
    return false;
  }
};

// 从token中获取用户信息
export const getUserInfo = () => {
  const token = getToken();
  if (!token) return null;
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return {
      id: payload.sub,
      username: payload.username,
      // 可以根据需要添加更多字段
    };
  } catch (error) {
    console.warn('Failed to parse user info from token:', error);
    return null;
  }
};

// 登出功能
export const logout = () => {
  removeToken();
  // 可以在这里添加其他登出逻辑，如清除其他存储的数据
};
