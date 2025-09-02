// src/api/models.ts
import api from './request';

export type ModelApiType = 'openai' | 'google_genai' | 'openai_compatible' | 'ollama' | 'anthropic';

export interface ProviderInfo {
  model: string;
  api_type: ModelApiType;
  base_url?: string;
  api_key?: string;
}

export interface ModelParams {
  temperature?: number;
  max_tokens: number;
  top_p?: number;
  stop?: string[];
  [key: string]: unknown; // For extra provider-specific parameters
}

export interface ModelCapabilities {
  context_window: number;
  support_tools: boolean;
  support_images: boolean;
  support_structure_output: boolean;
  built_in_tools: Record<string, string>;
}

export interface Model {
  id: string;
  name: string;
  description?: string;
  owner: string;
  provider: ProviderInfo;
  default_params: ModelParams;
  capabilities: ModelCapabilities;
}

export interface ModelRequest {
  name: string;
  description?: string;
  provider: ProviderInfo;
  default_params: ModelParams;
  capabilities: ModelCapabilities;
}

export interface ModelDeleteResponse {
  success: boolean;
  message: string;
}

// Get a specific model
export async function getModel(userId: string, modelId: string): Promise<Model> {
  const res = await api.get(`/api/models/user/${userId}/${modelId}`);
  return res.data;
}

// List models for a user
export async function getUserModels(userId: string): Promise<Model[]> {
  const res = await api.get(`/api/models/user/${userId}`);
  return res.data;
}

// Add a new model
export async function addModel(model: ModelRequest): Promise<Model> {
  const res = await api.post('/api/models/', model);
  return res.data;
}

// Update an existing model
export async function updateModel(userId: string, modelId: string, updates: ModelRequest): Promise<Model> {
  const res = await api.patch(`/api/models/user/${userId}/${modelId}`, updates);
  return res.data;
}

// Delete a model
export async function deleteModel(userId: string, modelId: string): Promise<ModelDeleteResponse> {
  const res = await api.delete(`/api/models/user/${userId}/${modelId}`);
  return res.data;
}
