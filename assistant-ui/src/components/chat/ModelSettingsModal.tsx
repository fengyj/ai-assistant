import React, { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { CpuChipIcon, UserIcon } from '@heroicons/react/24/outline';
import type { Model } from '../../api/models';

interface ModelSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  model: Model | null;
}

export const ModelSettingsModal: React.FC<ModelSettingsModalProps> = ({
  isOpen,
  onClose,
  model,
}) => {
  // 模拟一些模型参数设置
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [topP, setTopP] = useState(0.9);

  if (!isOpen) return null;

  const getModelTypeIcon = (model: Model) => {
    return model.owner === 'system' ? (
      <CpuChipIcon className="w-5 h-5 text-blue-500" />
    ) : (
      <UserIcon className="w-5 h-5 text-green-500" />
    );
  };

  const handleSave = () => {
    // TODO: 实现保存设置的逻辑
    console.log('保存模型设置:', {
      modelId: model?.id,
      temperature,
      maxTokens,
      topP,
    });
    onClose();
  };

  const handleReset = () => {
    setTemperature(0.7);
    setMaxTokens(2048);
    setTopP(0.9);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* 背景遮罩 */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50" 
        onClick={onClose}
      />
      
      {/* 模态框内容 */}
      <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md mx-4 max-h-[80vh] overflow-y-auto">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            {model && getModelTypeIcon(model)}
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              模型设置
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* 内容 */}
        <div className="p-4 space-y-6">
          {/* 模型信息 */}
          {model && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                当前模型
              </h3>
              <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-2">
                  {getModelTypeIcon(model)}
                  <span className="font-medium text-gray-900 dark:text-white">
                    {model.name}
                  </span>
                </div>
                {model.description && (
                  <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
                    {model.description}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* 参数设置 */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              参数设置
            </h3>

            {/* Temperature */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <label className="text-sm text-gray-600 dark:text-gray-300">
                  Temperature
                </label>
                <span className="text-sm text-gray-900 dark:text-white font-mono">
                  {temperature}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>保守 (0)</span>
                <span>创新 (2)</span>
              </div>
            </div>

            {/* Max Tokens */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <label className="text-sm text-gray-600 dark:text-gray-300">
                  最大 Token 数
                </label>
                <span className="text-sm text-gray-900 dark:text-white font-mono">
                  {maxTokens}
                </span>
              </div>
              <input
                type="range"
                min="256"
                max="4096"
                step="256"
                value={maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>256</span>
                <span>4096</span>
              </div>
            </div>

            {/* Top P */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <label className="text-sm text-gray-600 dark:text-gray-300">
                  Top P
                </label>
                <span className="text-sm text-gray-900 dark:text-white font-mono">
                  {topP}
                </span>
              </div>
              <input
                type="range"
                min="0.1"
                max="1"
                step="0.1"
                value={topP}
                onChange={(e) => setTopP(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>0.1</span>
                <span>1.0</span>
              </div>
            </div>
          </div>

          {/* 说明文本 */}
          <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
            <p><strong>Temperature:</strong> 控制输出的随机性，值越高越创新。</p>
            <p><strong>Max Tokens:</strong> 生成的最大 token 数量。</p>
            <p><strong>Top P:</strong> 核采样参数，控制词汇选择的多样性。</p>
          </div>
        </div>

        {/* 底部按钮 */}
        <div className="flex justify-between p-4 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={handleReset}
            className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white"
          >
            重置默认
          </button>
          <div className="flex space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white"
            >
              取消
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
            >
              保存
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
