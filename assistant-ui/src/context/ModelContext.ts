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

import type { Model } from '../api/models';

export interface ModelContextData {
	models: Model[];
	isLoadingModels: boolean;
	selectedModel: Model | null;
	selectedModelId: string | undefined;
	modelInfo: ModelInfo | null;
	isLoadingModelInfo: boolean;
	selectModel: (modelId: string) => void;
	refreshModels: () => Promise<void>;
	refreshModelInfo: () => Promise<void>;
}

import { createContext } from 'react';
export const ModelContext = createContext<ModelContextData | undefined>(undefined);
