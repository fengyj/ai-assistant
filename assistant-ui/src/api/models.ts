// src/api/models.ts
import api from './request';

export interface Model {
  id: string;
  name: string;
  type: string;
  description: string;
  owner: string;
  default_params: Record<string, unknown>;
  // ...other fields as needed
}

export async function getUserModels(userId: string): Promise<Model[]> {
  const res = await api.get(`/api/models/user/${userId}`);
  return res.data;
}
