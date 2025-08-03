
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
  
  const [currentResponseTimeout, setCurrentResponseTimeout] = useState<NodeJS.Timeout | null>(null);

  const generateId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;

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

  // 取消AI响应
  const cancelResponse = useCallback(() => {
    if (currentResponseTimeout) {
      clearTimeout(currentResponseTimeout);
      setCurrentResponseTimeout(null);
      setIsLoading(false);
    }
  }, [currentResponseTimeout]);

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
      const timeout = setTimeout(() => {
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
        setCurrentResponseTimeout(null); // 清除超时状态
      }, 1000 + Math.random() * 2000); // 模拟网络延迟

      // 保存当前的超时ID，以便能够取消
      setCurrentResponseTimeout(timeout);

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
    if (!currentConversation) return;

    const messageIndex = currentConversation.messages.findIndex(msg => msg.id === messageId);
    if (messageIndex === -1) return;

    const message = currentConversation.messages[messageIndex];
    if (message.role !== 'assistant') return; // 只能重新生成AI消息

    setIsLoading(true);

    try {
      // 移除当前AI消息及其后面的所有消息
      const messagesBeforeRegenerate = currentConversation.messages.slice(0, messageIndex);
      
      // 更新对话，移除旧的AI回复
      const tempConversation: Conversation = {
        ...currentConversation,
        messages: messagesBeforeRegenerate,
        updatedAt: new Date()
      };

      setCurrentConversation(tempConversation);
      setConversations(prev =>
        prev.map(c => c.id === currentConversation.id ? tempConversation : c)
      );

      // 模拟重新生成AI回复
      const timeout = setTimeout(() => {
        const newAiMessage: Message = {
          id: generateId(),
          content: `重新生成的回复：这是一个新的AI响应，内容与之前不同。重新生成功能可以为用户提供不同的回答选项。`,
          role: 'assistant',
          timestamp: new Date(),
          conversationId: currentConversation.id,
          metadata: {
            model: 'GPT-4',
            tokens: 45,
            regenerated: true
          }
        };

        const finalConversation: Conversation = {
          ...tempConversation,
          messages: [...tempConversation.messages, newAiMessage],
          updatedAt: new Date()
        };

        setCurrentConversation(finalConversation);
        setConversations(prev =>
          prev.map(c => c.id === currentConversation.id ? finalConversation : c)
        );
        setIsLoading(false);
        setCurrentResponseTimeout(null); // 清除超时状态
      }, 1000 + Math.random() * 2000);

      // 保存当前的超时ID，以便能够取消
      setCurrentResponseTimeout(timeout);

    } catch (error) {
      console.error('重新生成消息失败:', error);
      setIsLoading(false);
    }
  }, [currentConversation]);

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
    cancelResponse,
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
