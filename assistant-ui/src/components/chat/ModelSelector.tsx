import React, { useState, useRef, useEffect, useCallback } from 'react';
import { ChevronDownIcon, CpuChipIcon, UserIcon } from '@heroicons/react/24/outline';
import type { Model } from '../../api/models';

interface ModelSelectorProps {
  models: Model[];
  selectedModelId?: string;
  onModelChange: (modelId: string) => void;
  className?: string;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  selectedModelId,
  onModelChange,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState<'bottom' | 'top'>('bottom');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const selectedModel = models.find(m => m.id === selectedModelId);

  // 计算下拉菜单位置
  const calculateDropdownPosition = useCallback(() => {
    if (!buttonRef.current) return;

    const buttonRect = buttonRef.current.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const dropdownHeight = Math.min(256, models.length * 60); // 估算下拉菜单高度
    
    // 检查向下展开是否有足够空间
    const spaceBelow = viewportHeight - buttonRect.bottom;
    const spaceAbove = buttonRect.top;
    
    // 如果下方空间不足且上方空间更充足，则向上展开
    if (spaceBelow < dropdownHeight && spaceAbove > spaceBelow) {
      setDropdownPosition('top');
    } else {
      setDropdownPosition('bottom');
    }
  }, [models.length]);

  // 点击外部关闭下拉菜单和窗口大小改变时重新计算位置
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    const handleResize = () => {
      if (isOpen) {
        calculateDropdownPosition();
      }
    };

    const handleScroll = () => {
      if (isOpen) {
        calculateDropdownPosition();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    window.addEventListener('resize', handleResize);
    window.addEventListener('scroll', handleScroll, true);
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('scroll', handleScroll, true);
    };
  }, [isOpen, calculateDropdownPosition]);

  const handleToggle = () => {
    if (!isOpen) {
      calculateDropdownPosition();
    }
    setIsOpen(!isOpen);
  };

  const handleSelect = (modelId: string) => {
    onModelChange(modelId);
    setIsOpen(false);
  };

  const getModelTypeIcon = (model: Model) => {
    return model.owner === 'system' ? (
      <CpuChipIcon className="w-4 h-4 text-blue-500" />
    ) : (
      <UserIcon className="w-4 h-4 text-green-500" />
    );
  };

  const getModelTypeLabel = (model: Model) => {
    return model.owner === 'system' ? '系统' : '用户';
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* 选择器按钮 */}
      <button
        ref={buttonRef}
        type="button"
        className="model-selector-button"
        onClick={handleToggle}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <div className="flex items-center space-x-2 flex-1 min-w-0">
          {selectedModel && (
            <>
              {getModelTypeIcon(selectedModel)}
              <span className="truncate font-medium text-sm">
                {selectedModel.name}
              </span>
            </>
          )}
          {!selectedModel && (
            <span className="text-gray-500 text-sm">选择模型</span>
          )}
        </div>
        <ChevronDownIcon 
          className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`} 
        />
      </button>

      {/* 下拉菜单 */}
      {isOpen && (
        <div className={`model-selector-dropdown ${dropdownPosition === 'top' ? 'model-selector-dropdown-top' : 'model-selector-dropdown-bottom'}`}>
          <div className="model-selector-list" role="listbox">
            {models.map((model) => (
              <button
                key={model.id}
                type="button"
                className={`model-selector-option ${
                  selectedModelId === model.id ? 'model-selector-option-selected' : ''
                }`}
                onClick={() => handleSelect(model.id)}
                role="option"
                aria-selected={selectedModelId === model.id}
              >
                <div className="flex items-start justify-between w-full">
                  <div className="flex items-start space-x-2 flex-1 min-w-0">
                    {getModelTypeIcon(model)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center">
                        <span className="model-name font-medium text-sm truncate">
                          {model.name}
                        </span>
                      </div>
                      {model.description && (
                        <p className="model-description text-xs mt-1 line-clamp-2">
                          {model.description}
                        </p>
                      )}
                    </div>
                  </div>
                  <span className="chat-badge-small ml-2">
                    {getModelTypeLabel(model)}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
