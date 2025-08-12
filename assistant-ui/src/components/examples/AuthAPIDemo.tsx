// src/components/examples/AuthAPIDemo.tsx
import React, { useState } from 'react';
import { login, refreshToken, logout, type LoginRequest } from '../../api/auth';
import { useUserSession } from '../../hooks/useUserSession';

/**
 * 演示组件：展示重构后的认证 API 的使用方式
 */
export const AuthAPIDemo: React.FC = () => {
  const { user, isAuthenticated } = useUserSession();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<string>('');

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      setResult('请输入用户名和密码');
      return;
    }

    setIsLoading(true);
    setResult('');

    try {
      const credentials: LoginRequest = {
        username: username.trim(),
        password
      };

      const response = await login(credentials);
      setResult(`登录成功! 用户: ${response.user.username}, Token: ${response.access_token.substring(0, 20)}...`);
    } catch (error) {
      setResult(`登录失败: ${error instanceof Error ? error.message : '未知错误'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefreshToken = async () => {
    setIsLoading(true);
    setResult('');

    try {
      const response = await refreshToken(true);
      setResult(`Token 刷新成功! 新 Token: ${response.access_token.substring(0, 20)}..., 类型: ${response.token_type}`);
    } catch (error) {
      setResult(`Token 刷新失败: ${error instanceof Error ? error.message : '未知错误'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    setIsLoading(true);
    setResult('');

    try {
      await logout();
      setResult('注销成功!');
    } catch (error) {
      setResult(`注销失败: ${error instanceof Error ? error.message : '未知错误'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-sm border space-y-6 max-w-2xl">
      <h2 className="text-2xl font-bold text-gray-900">Auth API Demo</h2>
      
      {/* 当前状态 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">当前状态</h3>
        <p className="text-sm">
          <strong>认证状态:</strong> {isAuthenticated ? '✅ 已登录' : '❌ 未登录'}
        </p>
        {user && (
          <p className="text-sm">
            <strong>当前用户:</strong> {user.username} ({user.display_name})
          </p>
        )}
      </div>

      {/* 登录测试 */}
      {!isAuthenticated && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-green-900 mb-3">测试登录 API</h3>
          <div className="space-y-3">
            <input
              type="text"
              placeholder="用户名"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
              disabled={isLoading}
            />
            <input
              type="password"
              placeholder="密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
              disabled={isLoading}
            />
            <button
              onClick={handleLogin}
              disabled={isLoading}
              className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {isLoading ? '登录中...' : '测试 login() API'}
            </button>
          </div>
        </div>
      )}

      {/* 已登录时的操作 */}
      {isAuthenticated && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-yellow-900 mb-3">认证操作</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <button
              onClick={handleRefreshToken}
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? '处理中...' : '刷新 Token'}
            </button>
            <button
              onClick={handleLogout}
              disabled={isLoading}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
            >
              {isLoading ? '处理中...' : '注销'}
            </button>
          </div>
        </div>
      )}

      {/* 结果显示 */}
      {result && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">API 调用结果</h3>
          <pre className="text-sm text-gray-700 whitespace-pre-wrap break-words">
            {result}
          </pre>
        </div>
      )}

      {/* API 说明 */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">重构后的 Auth API</h3>
        <div className="text-sm text-gray-700 space-y-2">
          <div>
            <strong>login(credentials):</strong> 执行用户登录，自动存储认证数据
          </div>
          <div>
            <strong>refreshToken(extend_session):</strong> 刷新访问令牌
          </div>
          <div>
            <strong>logout():</strong> 注销用户并清除所有认证数据
          </div>
        </div>
        
        <h4 className="font-semibold mt-4 mb-2">重构优势:</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• <strong>集中管理:</strong> 所有认证 API 调用集中在 auth.ts 中</li>
          <li>• <strong>类型安全:</strong> 完整的 TypeScript 接口定义</li>
          <li>• <strong>一致性:</strong> 统一的错误处理和响应格式</li>
          <li>• <strong>可复用:</strong> 可在任何组件中导入使用</li>
          <li>• <strong>易维护:</strong> API 变更只需修改一个文件</li>
        </ul>
      </div>
    </div>
  );
};
