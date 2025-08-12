// src/components/examples/TokenManagementDemo.tsx
import React, { useState } from 'react';
import { useUserSession } from '../../hooks/useUserSession';
import { useAuthenticatedAPI } from '../../utils/apiHelpers';
import { getUserModels, type Model } from '../../api/models';

/**
 * 演示组件：展示主动 token 管理和认证 API 调用的最佳实践
 */
export const TokenManagementDemo: React.FC = () => {
  const { 
    user, 
    accessToken, 
    tokenType,
    sessionId, 
    expiryTime,
    isAuthenticated, 
    refreshToken,
    isTokenExpiringSoon,
    logout 
  } = useUserSession();

  const { 
    executeAuthenticatedRequest, 
    getAuthHeader
  } = useAuthenticatedAPI();

  const [models, setModels] = useState<Model[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastRefreshTime, setLastRefreshTime] = useState<Date | null>(null);

  if (!isAuthenticated) {
    return (
      <div className="p-6 bg-gray-50 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Token Management Demo</h2>
        <p className="text-gray-600">Please login to access this demo.</p>
      </div>
    );
  }

  const handleManualRefresh = async () => {
    setIsLoading(true);
    try {
      const newToken = await refreshToken();
      setLastRefreshTime(new Date());
      console.log('Manual refresh result:', newToken ? 'Success' : 'Failed');
    } catch (error) {
      console.error('Manual refresh error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFetchModels = async () => {
    if (!user?.id) return;
    
    setIsLoading(true);
    try {
      // 使用 executeAuthenticatedRequest 自动处理 token 刷新
      const userModels = await executeAuthenticatedRequest(getUserModels, user.id);
      setModels(userModels);
    } catch (error) {
      console.error('Failed to fetch models:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatExpiry = (time: number | null) => {
    if (!time) return 'N/A';
    const date = new Date(time);
    const now = new Date();
    const diffMs = time - now.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    
    return `${date.toLocaleTimeString()} (${diffMinutes > 0 ? `${diffMinutes}m remaining` : 'Expired'})`;
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-sm border space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Token Management Demo</h2>
      
      {/* Token Status Card */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">Token Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p><strong>User:</strong> {user?.username}</p>
            <p><strong>Token Type:</strong> {tokenType}</p>
            <p><strong>Has Token:</strong> {accessToken ? '✅ Yes' : '❌ No'}</p>
            <p><strong>Session ID:</strong> {sessionId ? '✅ Active' : '❌ None'}</p>
          </div>
          <div>
            <p><strong>Expires:</strong> {formatExpiry(expiryTime)}</p>
            <p><strong>Expiring Soon:</strong> {
              isTokenExpiringSoon() ? (
                <span className="text-orange-600 font-medium">⚠️ Yes</span>
              ) : (
                <span className="text-green-600">✅ No</span>
              )
            }</p>
            <p><strong>Auth Header:</strong></p>
            <code className="text-xs bg-gray-100 px-2 py-1 rounded block mt-1 break-all">
              {getAuthHeader() || 'Not available'}
            </code>
          </div>
        </div>
      </div>

      {/* Actions Card */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-green-900 mb-3">Actions</h3>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleManualRefresh}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Refreshing...' : 'Manual Token Refresh'}
          </button>
          
          <button
            onClick={handleFetchModels}
            disabled={isLoading}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Loading...' : 'Fetch Models (Auto-refresh)'}
          </button>
          
          <button
            onClick={logout}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
        
        {lastRefreshTime && (
          <p className="text-sm text-gray-600 mt-2">
            Last manual refresh: {lastRefreshTime.toLocaleTimeString()}
          </p>
        )}
      </div>

      {/* API Response Card */}
      {models.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Fetched Models ({models.length})
          </h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {models.map((model) => (
              <div key={model.id} className="bg-white p-2 rounded border text-sm">
                <div className="font-medium">{model.name}</div>
                <div className="text-gray-600 text-xs">{model.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Features Explanation */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-yellow-900 mb-3">What This Demo Shows</h3>
        <ul className="text-sm text-yellow-800 space-y-1">
          <li>• <strong>Proactive Token Refresh:</strong> Tokens are refreshed 5 minutes before expiry</li>
          <li>• <strong>Automatic Recovery:</strong> API calls automatically retry after token refresh</li>
          <li>• <strong>Persistent Storage:</strong> Token state is preserved across page reloads</li>
          <li>• <strong>Real-time Status:</strong> Token expiry status is monitored in real-time</li>
          <li>• <strong>Error Handling:</strong> Graceful handling of authentication failures</li>
          <li>• <strong>Type Safety:</strong> Full TypeScript support for all authentication APIs</li>
        </ul>
      </div>
    </div>
  );
};
