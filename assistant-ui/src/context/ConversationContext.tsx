import React, { useState, useCallback, useEffect } from 'react';
import { ConversationContext } from './ConversationContext';
import type { Conversation, Message } from '../types/index';

interface ConversationProviderProps {
  children: React.ReactNode;
}

export const ConversationProvider: React.FC<ConversationProviderProps> = ({ children }) => {
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // 生成唯一ID的工具函数
  const generateId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  // 创建新对话
  const createConversation = useCallback(async (title?: string): Promise<string> => {
    const newConversation: Conversation = {
      id: generateId(),
      title: title || '新对话',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    setConversations(prev => [newConversation, ...prev]);
    setCurrentConversation(newConversation);
    
    return newConversation.id;
  }, []);

  // 切换对话
  const switchConversation = useCallback(async (conversationId: string): Promise<void> => {
    const conversation = conversations.find(c => c.id === conversationId);
    if (conversation) {
      setCurrentConversation(conversation);
    }
  }, [conversations]);

  // 发送消息
  const sendMessage = useCallback(async (content: string, files?: File[]): Promise<void> => {
    if (!content.trim()) return;

    setIsLoading(true);
    
    try {
      // 如果没有当前对话，创建一个新的
      let conversation = currentConversation;
      if (!conversation) {
        const newConversationId = await createConversation();
        conversation = conversations.find(c => c.id === newConversationId) || null;
        if (!conversation) return;
      }

      // 创建用户消息
      const userMessage: Message = {
        id: generateId(),
        content,
        role: 'user',
        timestamp: new Date(),
        conversationId: conversation.id,
        metadata: files && files.length > 0 ? {
          files: files.map(file => ({
            id: generateId(),
            name: file.name,
            size: file.size,
            type: file.type,
          }))
        } : undefined
      };

      // 更新对话
      const updatedConversation: Conversation = {
        ...conversation,
        messages: [...conversation.messages, userMessage],
        updatedAt: new Date(),
        title: conversation.messages.length === 0 ? content.slice(0, 30) + (content.length > 30 ? '...' : '') : conversation.title
      };

      // 更新状态
      setCurrentConversation(updatedConversation);
      setConversations(prev => 
        prev.map(c => c.id === conversation!.id ? updatedConversation : c)
      );

      // 模拟AI回复（这里应该调用实际的API）
      setTimeout(() => {
        const aiMessage: Message = {
          id: generateId(),
          content: `这是对"${content}"的回复。这是一个模拟的AI响应，用于测试界面功能。在实际应用中，这里应该调用AI API来获取真实的回复。`,
          role: 'assistant',
          timestamp: new Date(),
          conversationId: conversation!.id,
          metadata: {
            model: 'GPT-4',
            tokens: 50
          }
        };

        const finalConversation: Conversation = {
          ...updatedConversation,
          messages: [...updatedConversation.messages, aiMessage],
          updatedAt: new Date()
        };

        setCurrentConversation(finalConversation);
        setConversations(prev => 
          prev.map(c => c.id === conversation!.id ? finalConversation : c)
        );
        setIsLoading(false);
      }, 1000 + Math.random() * 2000); // 模拟网络延迟

    } catch (error) {
      console.error('发送消息失败:', error);
      setIsLoading(false);
    }
  }, [currentConversation, conversations, createConversation]);

  // 编辑消息
  const editMessage = useCallback(async (messageId: string, newContent: string): Promise<void> => {
    if (!currentConversation) return;

    const updatedMessages = currentConversation.messages.map(msg =>
      msg.id === messageId ? { ...msg, content: newContent } : msg
    );

    const updatedConversation: Conversation = {
      ...currentConversation,
      messages: updatedMessages,
      updatedAt: new Date()
    };

    setCurrentConversation(updatedConversation);
    setConversations(prev =>
      prev.map(c => c.id === currentConversation.id ? updatedConversation : c)
    );
  }, [currentConversation]);

  // 删除消息
  const deleteMessage = useCallback(async (messageId: string): Promise<void> => {
    if (!currentConversation) return;

    const updatedMessages = currentConversation.messages.filter(msg => msg.id !== messageId);
    const updatedConversation: Conversation = {
      ...currentConversation,
      messages: updatedMessages,
      updatedAt: new Date()
    };

    setCurrentConversation(updatedConversation);
    setConversations(prev =>
      prev.map(c => c.id === currentConversation.id ? updatedConversation : c)
    );
  }, [currentConversation]);

  // 重新生成消息
  const regenerateMessage = useCallback(async (messageId: string): Promise<void> => {
    // 实现重新生成逻辑
    console.log('重新生成消息:', messageId);
  }, []);

  // 删除对话
  const deleteConversation = useCallback(async (conversationId: string): Promise<void> => {
    setConversations(prev => prev.filter(c => c.id !== conversationId));
    if (currentConversation?.id === conversationId) {
      setCurrentConversation(null);
    }
  }, [currentConversation]);

  // 更新对话标题
  const updateConversationTitle = useCallback(async (conversationId: string, title: string): Promise<void> => {
    setConversations(prev =>
      prev.map(c => c.id === conversationId ? { ...c, title, updatedAt: new Date() } : c)
    );
    
    if (currentConversation?.id === conversationId) {
      setCurrentConversation(prev => prev ? { ...prev, title, updatedAt: new Date() } : null);
    }
  }, [currentConversation]);

  // 清空当前对话
  const clearCurrentConversation = useCallback(() => {
    setCurrentConversation(null);
  }, []);

  // 根据ID获取消息
  const getMessageById = useCallback((messageId: string): Message | null => {
    if (!currentConversation) return null;
    return currentConversation.messages.find(msg => msg.id === messageId) || null;
  }, [currentConversation]);

  // 初始化时创建一个默认对话
  useEffect(() => {
    if (conversations.length === 0) {
      createConversation('欢迎对话');
    }
  }, [conversations.length, createConversation]);

  const value = {
    currentConversation,
    conversations,
    isLoading,
    sendMessage,
    editMessage,
    deleteMessage,
    regenerateMessage,
    createConversation,
    switchConversation,
    deleteConversation,
    updateConversationTitle,
    clearCurrentConversation,
    getMessageById,
  };

  return (
    <ConversationContext.Provider value={value}>
      {children}
    </ConversationContext.Provider>
  );
};
