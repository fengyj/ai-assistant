import React from 'react';
import { useSidebar } from '../../hooks/useSidebar';

interface MainLayoutProps {
  sidebar: React.ReactNode;
  main: React.ReactNode;
  className?: string;
}

export const MainLayout: React.FC<MainLayoutProps> = ({
  sidebar,
  main,
  className = '',
}) => {
  const { isCollapsed, isMobileOpen, setMobileOpen } = useSidebar();

  const handleOverlayClick = () => {
    setMobileOpen(false);
  };

  return (
    <div className={`main-layout ${className}`}>
      {/* 移动端遮罩层 */}
      {isMobileOpen && (
        <div 
          className="sidebar-overlay"
          onClick={handleOverlayClick}
        />
      )}
      
      {/* 左侧侧边栏 */}
      <div className={`sidebar-container ${isCollapsed ? 'collapsed' : ''} ${isMobileOpen ? 'mobile-open' : ''}`}>
        {sidebar}
      </div>
      
      {/* 右侧主内容区 */}
      <div className="main-content">
        {main}
      </div>
    </div>
  );
};
