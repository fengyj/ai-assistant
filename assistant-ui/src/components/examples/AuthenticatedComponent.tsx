// src/components/examples/AuthenticatedComponent.tsx
import React, { useState, useEffect } from 'react';
import { useUserSession } from '../../hooks/useUserSession';
import { getUserModels, type Model } from '../../api/models';

/**
 * 示例组件：展示如何使用 UserSessionContext 获取认证信息和调用 API
 */
export const AuthenticatedComponent: React.FC = () => {
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

  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 获取模型列表的函数
  const fetchModels = async () => {
    if (!user?.id || !isAuthenticated) {
      setError('User not authenticated');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const userModels = await getUserModels(user.id);
      setModels(userModels);
    } catch (err) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { status?: number } };
        if (axiosError.response?.status === 401) {
          // Token 可能过期，尝试刷新
          console.log('Token expired, attempting to refresh...');
          try {
            const newToken = await refreshToken();
            if (newToken) {
              // 重试获取模型
              const userModels = await getUserModels(user.id);
              setModels(userModels);
            } else {
              setError('Authentication failed. Please login again.');
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            setError('Authentication failed. Please login again.');
          }
        } else {
          setError('Failed to fetch models');
        }
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  // 当用户信息变化时自动获取模型
  useEffect(() => {
    if (user?.id && isAuthenticated) {
      fetchModels();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id, isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="p-4">
        <p className="text-gray-600">Please login to view this content.</p>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div className="bg-blue-50 p-3 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">Authentication Status</h3>
        <div className="space-y-1 text-sm">
          <p><strong>User:</strong> {user?.username} ({user?.display_name})</p>
          <p><strong>User ID:</strong> {user?.id}</p>
          <p><strong>Has Access Token:</strong> {accessToken ? 'Yes' : 'No'}</p>
          <p><strong>Token Type:</strong> {tokenType || 'Not set'}</p>
          <p><strong>Has Session ID:</strong> {sessionId ? 'Yes' : 'No'}</p>
          <p><strong>Is Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</p>
          <p><strong>Token Expiry:</strong> {
            expiryTime 
              ? new Date(expiryTime).toLocaleString() 
              : 'Not available'
          }</p>
          <p><strong>Token Expiring Soon:</strong> {
            isTokenExpiringSoon() ? (
              <span className="text-orange-600 font-medium">Yes (&lt; 5 minutes)</span>
            ) : (
              <span className="text-green-600">No</span>
            )
          }</p>
          {accessToken && tokenType && (
            <p><strong>Auth Header:</strong> 
              <code className="ml-1 text-xs bg-gray-100 px-1 rounded">
                {tokenType} {accessToken.substring(0, 20)}...
              </code>
            </p>
          )}
        </div>
      </div>

      <div className="bg-green-50 p-3 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">Available Models</h3>
        
        {loading && <p className="text-gray-600">Loading models...</p>}
        
        {error && (
          <div className="text-red-600 mb-2">
            <p>Error: {error}</p>
            <button 
              onClick={fetchModels}
              className="mt-2 px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
            >
              Retry
            </button>
          </div>
        )}
        
        {models.length > 0 && (
          <div className="space-y-2">
            {models.map((model) => (
              <div key={model.id} className="border border-gray-200 p-2 rounded">
                <h4 className="font-medium">{model.name}</h4>
                <p className="text-sm text-gray-600">{model.description}</p>
              </div>
            ))}
          </div>
        )}
        
        {!loading && !error && models.length === 0 && (
          <p className="text-gray-600">No models available</p>
        )}
      </div>

      <div className="bg-red-50 p-3 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">Actions</h3>
        <div className="space-x-2">
          <button 
            onClick={fetchModels}
            disabled={loading}
            className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50"
          >
            Refresh Models
          </button>
          <button 
            onClick={logout}
            className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  );
};
