import { useState } from 'react';
import type { User } from '../types';

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);

  const login = (username: string, password: string): boolean => {
    // 模拟登录逻辑
    if (username && password) {
      setUser({
        id: '1',
        name: username,
        avatar: `https://api.dicebear.com/7.x/avatars/svg?seed=${username}`
      });
      return true;
    }
    return false;
  };

  const logout = () => {
    setUser(null);
  };

  return {
    user,
    login,
    logout,
    isAuthenticated: !!user
  };
};
