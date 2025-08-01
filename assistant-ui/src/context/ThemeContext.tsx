import React, { useEffect, useState } from 'react';
import { ThemeContext } from './ThemeContext';
import type { Theme } from '../types/index';

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // 使用懒初始化避免在SSR中出现问题
  const [theme, setTheme] = useState<Theme>(() => {
    // 检查localStorage中的偏好设置
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('theme') as Theme | null;
      if (savedTheme === 'dark' || savedTheme === 'light') {
        return savedTheme;
      }
      // 如果没有保存的设置，检查系统偏好
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
    }
    return 'light';
  });

  // 应用主题到DOM
  useEffect(() => {
    const root = document.documentElement;
    
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    // 保存到localStorage
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
