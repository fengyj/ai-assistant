// src/components/ui/LoadingSpinner.tsx
import React from 'react';

interface LoadingSpinnerProps {
  /** 加载文本，默认为 "加载中..." */
  text?: string;
  /** 尺寸大小 */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** 是否显示全屏加载 */
  fullScreen?: boolean;
  /** 自定义类名 */
  className?: string;
  /** 是否显示背景 */
  showBackground?: boolean;
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
  xl: 'h-16 w-16'
};

const textSizeClasses = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
  xl: 'text-xl'
};

/**
 * 通用加载指示器组件
 * 支持不同尺寸、全屏模式、自定义文本等
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  text = '加载中...',
  size = 'md',
  fullScreen = false,
  className = '',
  showBackground = true
}) => {
  const content = (
    <div className={`centered-container flex-col ${className}`}>
      {/* 旋转加载图标 */}
      <div
        className={`animate-spin rounded-full border-b-2 border-blue-500 ${sizeClasses[size]} mb-3`}
        role="status"
        aria-label="加载中"
      />
      
      {/* 加载文本 */}
      {text && (
        <p className={`text-gray-600 dark:text-gray-400 ${textSizeClasses[size]} font-medium`}>
          {text}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className={`centered-container fixed inset-0 z-50 ${
        showBackground 
          ? 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm' 
          : ''
      }`}>
        {content}
      </div>
    );
  }

  return (
    <div className={`centered-container p-8 ${
      showBackground 
        ? 'bg-gray-50 dark:bg-gray-800 rounded-lg' 
        : ''
    }`}>
      {content}
    </div>
  );
};
