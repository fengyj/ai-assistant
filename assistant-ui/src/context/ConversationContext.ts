import { createContext } from 'react';
import type { Conversation, Message, MessageMetadata } from '../types/index';

export interface ConversationContextType {
  // 当前对话状态
  currentConversation: Conversation | null;
  conversations: Conversation[];
  isLoading: boolean;
  
  // 消息相关操作
  sendMessage: (content: string, files?: File[]) => Promise<void>;
  cancelResponse: () => void;
  editMessage: (messageId: string, newContent: string) => Promise<void>;
  deleteMessage: (messageId: string) => Promise<void>;
  regenerateMessage: (messageId: string) => Promise<void>;
  
  // 对话相关操作
  createConversation: (title?: string) => Promise<string>;
  switchConversation: (conversationId: string) => Promise<void>;
  deleteConversation: (conversationId: string) => Promise<void>;
  updateConversationTitle: (conversationId: string, title: string) => Promise<void>;
  
  // 工具函数
  clearCurrentConversation: () => void;
  getMessageById: (messageId: string) => Message | null;
  updateMessageMetadata: (messageId: string, metadata: Partial<MessageMetadata>) => void;
}

export const ConversationContext = createContext<ConversationContextType | null>(null);
