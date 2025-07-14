// Types for the AI Assistant application

export interface User {
  id: string;
  name: string;
  avatar?: string;
  email?: string;
}

export interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  isLoading?: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface AIModel {
  id: string;
  name: string;
  description: string;
  isAvailable: boolean;
  settings?: Record<string, any>;
}

export interface AppState {
  user: User | null;
  conversations: Conversation[];
  currentConversation: Conversation | null;
  selectedModel: AIModel | null;
  availableModels: AIModel[];
  theme: 'light' | 'dark';
  isLoading: boolean;
}
