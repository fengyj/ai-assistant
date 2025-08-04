import React from 'react';

// 用户相关类型
export interface User {
  id: string;
  name: string;
  email?: string;
  avatar?: string;
  isLoggedIn: boolean;
}

// 消息元数据类型
export interface MessageMetadata {
  model?: string;
  tokens?: number;
  files?: FileAttachment[];
  regenerated?: boolean;
  liked?: boolean;
  disliked?: boolean;
}

// 消息相关类型
export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  conversationId: string;
  metadata?: MessageMetadata;
}

// 对话相关类型
export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  userId?: string;
}

// 文件附件类型
export interface FileAttachment {
  id: string;
  name: string;
  size: number;
  type: string;
  url?: string;
  data?: string; // base64 for images
}

// 主题相关类型
export type Theme = 'light' | 'dark';

// UI状态类型
export interface UIState {
  sidebarCollapsed: boolean;
  currentConversationId: string | null;
  isLoading: boolean;
  notifications: Notification[];
}

// 通知类型
export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error';
  message: string;
  timestamp: Date;
}

// API相关类型
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface SendMessageRequest {
  content: string;
  conversationId?: string;
  files?: FileAttachment[];
  model?: string;
}

export interface SendMessageResponse {
  message: Message;
  conversation: Conversation;
}

// 模型配置类型
export interface ModelConfig {
  id: string;
  name: string;
  provider: string;
  maxTokens: number;
  available: boolean;
}

// 组件Props类型
export interface ComponentProps {
  className?: string;
  children?: React.ReactNode;
}
