import React, { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

/**
 * 通用 Input 组件，支持单行输入和错误提示
 */
const Input = forwardRef<HTMLInputElement, InputProps>(({ label, error, className = '', ...props }, ref) => (
  <div className={`w-full ${className}`}>
    {label && <label className="block mb-1 text-sm text-gray-700 dark:text-gray-300">{label}</label>}
    <input
      ref={ref}
      className="ui-input"
      {...props}
    />
    {error && <div className="mt-1 text-xs text-red-600 dark:text-red-400">{error}</div>}
  </div>
));

Input.displayName = 'Input';

export default Input;
