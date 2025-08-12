// src/components/ui/AppInitializing.tsx
import React from 'react';
import { LoadingSpinner } from './LoadingSpinner';

interface AppInitializingProps {
  /** 自定义加载文本 */
  message?: string;
  /** 是否显示详细状态 */
  showDetails?: boolean;
}

/**
 * 应用初始化加载组件
 * 专门用于应用启动时的认证状态恢复和初始化过程
 */
export const AppInitializing: React.FC<AppInitializingProps> = ({
  message = '正在初始化...',
  showDetails = false
}) => {
  return (
    <div className="centered-page min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="text-center max-w-md mx-auto px-4">
        {/* Logo 或品牌区域 */}
        <div className="mb-8">
          <div className="icon-container mx-auto w-16 h-16 bg-blue-500">
            <span className="text-white text-2xl font-bold">AI</span>
          </div>
          <h1 className="mt-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">
            AI Assistant
          </h1>
        </div>

        {/* 加载指示器 */}
        <LoadingSpinner 
          text={message} 
          size="lg" 
          showBackground={false}
        />

        {/* 详细状态信息 */}
        {showDetails && (
          <div className="mt-6 space-y-2 text-sm text-gray-500 dark:text-gray-400">
            <p>正在恢复用户会话...</p>
            <p>检查认证状态...</p>
            <p>初始化应用配置...</p>
          </div>
        )}

        {/* 底部提示 */}
        <div className="mt-8 text-xs text-gray-400 dark:text-gray-500">
          <p>首次启动可能需要几秒钟</p>
        </div>
      </div>
    </div>
  );
};
