// src/components/ui/LoadingButton.tsx
import React from 'react';

interface LoadingButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** 是否显示加载状态 */
  loading?: boolean;
  /** 加载状态下的文本 */
  loadingText?: string;
  /** 加载图标位置 */
  iconPosition?: 'left' | 'right';
  /** 按钮变体 */
  variant?: 'primary' | 'secondary' | 'danger' | 'outline';
  /** 按钮尺寸 */
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

const variantClasses = {
  primary: 'bg-blue-500 hover:bg-blue-600 text-white border-blue-500',
  secondary: 'bg-gray-500 hover:bg-gray-600 text-white border-gray-500',
  danger: 'bg-red-500 hover:bg-red-600 text-white border-red-500',
  outline: 'bg-transparent hover:bg-gray-50 text-gray-700 border-gray-300 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-800'
};

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg'
};

const spinnerSizeClasses = {
  sm: 'h-3 w-3',
  md: 'h-4 w-4',
  lg: 'h-5 w-5'
};

/**
 * 带加载状态的按钮组件
 * 在执行异步操作时显示加载指示器
 */
export const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading = false,
  loadingText,
  iconPosition = 'left',
  variant = 'primary',
  size = 'md',
  disabled,
  className = '',
  children,
  ...props
}) => {
  const isDisabled = disabled || loading;
  
  const spinner = (
    <div
      className={`animate-spin rounded-full border-2 border-transparent border-t-current ${spinnerSizeClasses[size]}`}
      aria-hidden="true"
    />
  );

  const content = loading && loadingText ? loadingText : children;

  return (
    <button
      {...props}
      disabled={isDisabled}
      className={`
        relative inline-flex items-center justify-center font-medium rounded-md border transition-colors duration-200
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      {/* 左侧加载图标 */}
      {loading && iconPosition === 'left' && (
        <span className="mr-2">
          {spinner}
        </span>
      )}
      
      {/* 按钮内容 */}
      <span className={loading ? 'opacity-90' : ''}>
        {content}
      </span>
      
      {/* 右侧加载图标 */}
      {loading && iconPosition === 'right' && (
        <span className="ml-2">
          {spinner}
        </span>
      )}
    </button>
  );
};
