import React, { createContext, useState, useEffect, useCallback } from 'react';
import { getUserModels, type Model } from '../api/models';
import { useUserSession } from '../hooks/useUserSession';

// 模型信息接口
export interface ModelInfo {
  tokenUsage?: {
    total: number;
    used: number;
    remaining: number;
  };
  performance?: {
    averageResponseTime: number;
    successRate: number;
  };
  lastUsed?: Date;
  // 其他模型信息可以在这里扩展
}

// Context 数据类型
export interface ModelContextData {
  // 模型列表
  models: Model[];
  isLoadingModels: boolean;
  
  // 当前选中的模型
  selectedModel: Model | null;
  selectedModelId: string | undefined;
  
  // 模型信息
  modelInfo: ModelInfo | null;
  isLoadingModelInfo: boolean;
  
  // 操作方法
  selectModel: (modelId: string) => void;
  refreshModels: () => Promise<void>;
  refreshModelInfo: () => Promise<void>;
}

const ModelContext = createContext<ModelContextData | undefined>(undefined);

// Provider 组件
interface ModelProviderProps {
  children: React.ReactNode;
}

export const ModelProvider: React.FC<ModelProviderProps> = ({ children }) => {
  const { user } = useUserSession();
  const userId = user?.id;

  // State
  const [models, setModels] = useState<Model[]>([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [selectedModelId, setSelectedModelId] = useState<string | undefined>();
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [isLoadingModelInfo, setIsLoadingModelInfo] = useState(false);

  // 计算选中的模型
  const selectedModel = models.find(m => m.id === selectedModelId) || null;

  // 加载模型列表
  const refreshModels = useCallback(async () => {
    if (!userId) return;

    setIsLoadingModels(true);
    try {
      const cacheKey = 'user_models';
      const cached = localStorage.getItem(cacheKey);
      
      // 先尝试从缓存加载
      if (cached) {
        const cachedModels = JSON.parse(cached) as Model[];
        setModels(cachedModels);
        if (!selectedModelId && cachedModels.length > 0) {
          setSelectedModelId(cachedModels[0].id);
        }
      }

      // 然后从 API 获取最新数据
      const fetchedModels = await getUserModels(userId);
      setModels(fetchedModels);
      localStorage.setItem(cacheKey, JSON.stringify(fetchedModels));
      
      // 如果没有选中模型，选择第一个
      if (!selectedModelId && fetchedModels.length > 0) {
        setSelectedModelId(fetchedModels[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
    } finally {
      setIsLoadingModels(false);
    }
  }, [userId]);

  // 加载模型信息（暂时为模拟实现）
  const refreshModelInfo = useCallback(async () => {
    if (!selectedModelId) {
      setModelInfo(null);
      return;
    }

    setIsLoadingModelInfo(true);
    try {
      // TODO: 这里应该调用实际的 API 获取模型信息
      // 现在先用模拟数据
      await new Promise(resolve => setTimeout(resolve, 500)); // 模拟网络延迟
      
      const mockModelInfo: ModelInfo = {
        tokenUsage: {
          total: 100000,
          used: Math.floor(Math.random() * 50000),
          remaining: 50000,
        },
        performance: {
          averageResponseTime: Math.floor(Math.random() * 2000) + 500,
          successRate: 0.95 + Math.random() * 0.05,
        },
        lastUsed: new Date(),
      };
      
      setModelInfo(mockModelInfo);
    } catch (error) {
      console.error('Failed to fetch model info:', error);
      setModelInfo(null);
    } finally {
      setIsLoadingModelInfo(false);
    }
  }, [selectedModelId]);

  // 选择模型
  const selectModel = useCallback((modelId: string) => {
    setSelectedModelId(modelId);
  }, []);

  // 初始加载模型列表
  useEffect(() => {
    refreshModels();
  }, [refreshModels]);

  // 当选中模型变化时，加载模型信息
  useEffect(() => {
    refreshModelInfo();
  }, [refreshModelInfo]);

  const value: ModelContextData = {
    models,
    isLoadingModels,
    selectedModel,
    selectedModelId,
    modelInfo,
    isLoadingModelInfo,
    selectModel,
    refreshModels,
    refreshModelInfo,
  };

  return (
    <ModelContext.Provider value={value}>
      {children}
    </ModelContext.Provider>
  );
};

// Export the context for use in hooks
export { ModelContext };
