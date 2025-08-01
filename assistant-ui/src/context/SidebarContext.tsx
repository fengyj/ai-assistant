import React, { useState, useEffect } from 'react';
import { SidebarContext } from './SidebarContext';

interface SidebarProviderProps {
  children: React.ReactNode;
}

export const SidebarProvider: React.FC<SidebarProviderProps> = ({ children }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  // 检测窗口大小变化，自动处理移动端显示
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setIsMobileOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleCollapse = () => {
    setIsCollapsed(prev => !prev);
  };

  const toggleMobileOpen = () => {
    setIsMobileOpen(prev => !prev);
  };

  const setMobileOpen = (open: boolean) => {
    setIsMobileOpen(open);
  };

  return (
    <SidebarContext.Provider
      value={{
        isCollapsed,
        isMobileOpen,
        toggleCollapse,
        toggleMobileOpen,
        setMobileOpen,
      }}
    >
      {children}
    </SidebarContext.Provider>
  );
};
