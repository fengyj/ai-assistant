import React, { useState } from 'react';
import { CogIcon, InformationCircleIcon } from '@heroicons/react/24/outline';
import { ModelSelector } from './ModelSelector';
import { useModel } from '../../hooks/useModel';
import { ModelInfoModal } from './ModelInfoModal';
import { ModelSettingsModal } from './ModelSettingsModal';

interface ModelControlProps {
  className?: string;
}

export const ModelControl: React.FC<ModelControlProps> = ({ className = '' }) => {
  const {
    models,
    selectedModelId,
    selectedModel,
    modelInfo,
    isLoadingModelInfo,
    selectModel,
    refreshModelInfo,
  } = useModel();

  // 模态框状态
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);

  const handleModelChange = (modelId: string) => {
    selectModel(modelId);
  };

  const handleInfoClick = () => {
    setShowInfoModal(true);
    // 点击时刷新模型信息
    refreshModelInfo();
  };

  const handleSettingsClick = () => {
    setShowSettingsModal(true);
  };

  return (
    <>
      <div className={`flex items-center space-x-2 ${className}`}>
        {/* 模型选择器 */}
        <ModelSelector
          models={models}
          selectedModelId={selectedModelId}
          onModelChange={handleModelChange}
          className="min-w-[160px]"
        />
        
        {/* Token使用统计按钮 */}
        <button 
          className="tool-icon-btn relative" 
          title="Token使用统计"
          onClick={handleInfoClick}
          disabled={!selectedModel}
        >
          <InformationCircleIcon className="w-3.5 h-3.5" />
          {isLoadingModelInfo && (
            <div className="chat-badge-status chat-badge-status--active" />
          )}
        </button>
        
        {/* 模型设置按钮 */}
        <button 
          className="tool-icon-btn" 
          title="模型设置"
          onClick={handleSettingsClick}
          disabled={!selectedModel}
        >
          <CogIcon className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 模型信息模态框 */}
      <ModelInfoModal
        isOpen={showInfoModal}
        onClose={() => setShowInfoModal(false)}
        model={selectedModel}
        modelInfo={modelInfo}
        isLoading={isLoadingModelInfo}
        onRefresh={refreshModelInfo}
      />

      {/* 模型设置模态框 */}
      <ModelSettingsModal
        isOpen={showSettingsModal}
        onClose={() => setShowSettingsModal(false)}
        model={selectedModel}
      />
    </>
  );
};
