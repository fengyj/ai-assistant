import React from 'react';
import { XMarkIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { CpuChipIcon, UserIcon } from '@heroicons/react/24/outline';
import type { Model } from '../../api/models';
import type { ModelInfo } from '../../context/ModelContext';

interface ModelInfoModalProps {
  isOpen: boolean;
  onClose: () => void;
  model: Model | null;
  modelInfo: ModelInfo | null;
  isLoading: boolean;
  onRefresh: () => void;
}

export const ModelInfoModal: React.FC<ModelInfoModalProps> = ({
  isOpen,
  onClose,
  model,
  modelInfo,
  isLoading,
  onRefresh,
}) => {
  if (!isOpen) return null;

  const getModelTypeIcon = (model: Model) => {
    return model.owner === 'system' ? (
      <CpuChipIcon className="w-5 h-5 text-blue-500" />
    ) : (
      <UserIcon className="w-5 h-5 text-green-500" />
    );
  };

  const formatUsagePercentage = (used: number, total: number) => {
    return ((used / total) * 100).toFixed(1);
  };

  const formatResponseTime = (time: number) => {
    return time < 1000 ? `${time}ms` : `${(time / 1000).toFixed(1)}s`;
  };

  return (
    <div className="centered-container fixed inset-0 z-50">
      {/* 背景遮罩 */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50" 
        onClick={onClose}
      />
      
      {/* 模态框内容 */}
      <div className="modal-content w-full max-w-md mx-4 max-h-[80vh] overflow-y-auto">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            {model && getModelTypeIcon(model)}
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              模型信息
            </h2>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 disabled:opacity-50"
              title="刷新"
            >
              <ArrowPathIcon className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 内容 */}
        <div className="p-4 space-y-4">
          {/* 模型基本信息 */}
          {model && (
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                基本信息
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">名称:</span>
                  <span className="text-gray-900 dark:text-white font-medium">
                    {model.name}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">类型:</span>
                  <span className="text-gray-900 dark:text-white">
                    {model.type}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">所有者:</span>
                  <span className="text-gray-900 dark:text-white">
                    {model.owner === 'system' ? '系统' : '用户'}
                  </span>
                </div>
                {model.description && (
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">描述:</span>
                    <p className="text-gray-900 dark:text-white mt-1">
                      {model.description}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 分隔线 */}
          <div className="border-t border-gray-200 dark:border-gray-700" />

          {/* Token 使用情况 */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Token 使用情况
            </h3>
            {isLoading ? (
              <div className="centered-container py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500" />
                <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">
                  加载中...
                </span>
              </div>
            ) : modelInfo?.tokenUsage ? (
              <div className="space-y-3">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">总量:</span>
                    <span className="text-gray-900 dark:text-white">
                      {modelInfo.tokenUsage.total.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">已使用:</span>
                    <span className="text-gray-900 dark:text-white">
                      {modelInfo.tokenUsage.used.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">剩余:</span>
                    <span className="text-gray-900 dark:text-white">
                      {modelInfo.tokenUsage.remaining.toLocaleString()}
                    </span>
                  </div>
                </div>
                
                {/* 使用率进度条 */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500 dark:text-gray-400">使用率</span>
                    <span className="text-gray-900 dark:text-white">
                      {formatUsagePercentage(modelInfo.tokenUsage.used, modelInfo.tokenUsage.total)}%
                    </span>
                  </div>
                  <div className="progress-bar-container">
                    <div 
                      className="progress-bar"
                      style={{ 
                        '--progress-width': `${formatUsagePercentage(modelInfo.tokenUsage.used, modelInfo.tokenUsage.total)}%` 
                      } as React.CSSProperties}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                暂无 Token 使用信息
              </p>
            )}
          </div>

          {/* 性能信息 */}
          {modelInfo?.performance && (
            <>
              <div className="border-t border-gray-200 dark:border-gray-700" />
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  性能信息
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">平均响应时间:</span>
                    <span className="text-gray-900 dark:text-white">
                      {formatResponseTime(modelInfo.performance.averageResponseTime)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">成功率:</span>
                    <span className="text-gray-900 dark:text-white">
                      {(modelInfo.performance.successRate * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* 最后使用时间 */}
          {modelInfo?.lastUsed && (
            <>
              <div className="border-t border-gray-200 dark:border-gray-700" />
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  使用记录
                </h3>
                <div className="text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">最后使用:</span>
                    <span className="text-gray-900 dark:text-white">
                      {modelInfo.lastUsed.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
