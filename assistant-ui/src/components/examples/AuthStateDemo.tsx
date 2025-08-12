// src/components/examples/AuthStateDemo.tsx
import React from 'react';
import { useUserSession } from '../../hooks/useUserSession';

/**
 * 演示组件：显示认证状态的详细信息，用于调试重新打开窗口的场景
 */
export const AuthStateDemo: React.FC = () => {
  const { 
    user, 
    isAuthenticated, 
    isInitializing,
    accessToken, 
    tokenType,
    sessionId, 
    expiryTime,
    isTokenExpiringSoon 
  } = useUserSession();

  const formatTime = (timestamp: number | null) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
  };

  const getTimeRemaining = (timestamp: number | null) => {
    if (!timestamp) return 'N/A';
    const now = Date.now();
    const remaining = timestamp - now;
    if (remaining <= 0) return 'Expired';
    
    const minutes = Math.floor(remaining / (1000 * 60));
    const seconds = Math.floor((remaining % (1000 * 60)) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  return (
    <div className="fixed top-4 right-4 bg-white border border-gray-300 rounded-lg p-4 shadow-lg max-w-sm z-50">
      <h3 className="text-lg font-semibold mb-3 text-gray-900">Auth State Debug</h3>
      
      <div className="space-y-2 text-sm">
        {/* 初始化状态 */}
        <div className="flex justify-between">
          <span className="font-medium text-gray-700">Initializing:</span>
          <span className={isInitializing ? 'text-orange-600' : 'text-green-600'}>
            {isInitializing ? '🔄 Yes' : '✅ No'}
          </span>
        </div>

        {/* 认证状态 */}
        <div className="flex justify-between">
          <span className="font-medium text-gray-700">Authenticated:</span>
          <span className={isAuthenticated ? 'text-green-600' : 'text-red-600'}>
            {isAuthenticated ? '✅ Yes' : '❌ No'}
          </span>
        </div>

        {/* 用户信息 */}
        <div className="flex justify-between">
          <span className="font-medium text-gray-700">User:</span>
          <span className="text-gray-600 truncate max-w-24">
            {user ? user.username : 'None'}
          </span>
        </div>

        {/* Token 状态 */}
        <div className="flex justify-between">
          <span className="font-medium text-gray-700">Has Token:</span>
          <span className={accessToken ? 'text-green-600' : 'text-red-600'}>
            {accessToken ? '✅ Yes' : '❌ No'}
          </span>
        </div>

        {/* Token 类型 */}
        <div className="flex justify-between">
          <span className="font-medium text-gray-700">Token Type:</span>
          <span className="text-gray-600">
            {tokenType || 'N/A'}
          </span>
        </div>

        {/* Session ID */}
        <div className="flex justify-between">
          <span className="font-medium text-gray-700">Session ID:</span>
          <span className={sessionId ? 'text-green-600' : 'text-red-600'}>
            {sessionId ? '✅ Yes' : '❌ No'}
          </span>
        </div>

        {/* Token 过期时间 */}
        <div className="border-t pt-2">
          <div className="text-xs text-gray-500 mb-1">Token Expiry:</div>
          <div className="text-xs text-gray-700">
            {formatTime(expiryTime)}
          </div>
          <div className="text-xs text-gray-700">
            Remaining: {getTimeRemaining(expiryTime)}
          </div>
        </div>

        {/* 即将过期状态 */}
        <div className="flex justify-between">
          <span className="font-medium text-gray-700">Expiring Soon:</span>
          <span className={isTokenExpiringSoon() ? 'text-orange-600' : 'text-green-600'}>
            {isTokenExpiringSoon() ? '⚠️ Yes' : '✅ No'}
          </span>
        </div>

        {/* 时间戳 */}
        <div className="border-t pt-2 text-xs text-gray-500">
          Current: {new Date().toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};
