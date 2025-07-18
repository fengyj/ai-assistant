import { useState, useEffect } from 'react';
import type { Conversation, Message } from '../types';

export const useConversations = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);

  // 初始化默认对话
  useEffect(() => {
    if (conversations.length === 0) {
      const now = new Date();
      const defaultConversations: Conversation[] = [
        {
          id: '1',
          title: 'New Chat',
          messages: [{
            id: '1',
            content: 'Hello! I\'m your AI assistant. How can I help you today?',
            isUser: false,
            timestamp: new Date()
          }],
          createdAt: new Date(),
          updatedAt: new Date()
        },
        {
          id: '2',
          title: '如何学习React',
          messages: [{
            id: '2',
            content: '请问如何快速学习React？',
            isUser: true,
            timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000)
          }],
          createdAt: new Date(now.getTime() - 2 * 60 * 60 * 1000),
          updatedAt: new Date(now.getTime() - 2 * 60 * 60 * 1000)
        }
      ];
      setConversations(defaultConversations);
      setCurrentConversationId('1');
    }
  }, [conversations.length]);

  const currentConversation = conversations.find(c => c.id === currentConversationId);

  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [{
        id: Date.now().toString(),
        content: 'Hello! I\'m your AI assistant. How can I help you today?',
        isUser: false,
        timestamp: new Date()
      }],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    setConversations(prev => [newConversation, ...prev]);
    setCurrentConversationId(newConversation.id);
  };

  const deleteConversation = (id: string) => {
    setConversations(prev => prev.filter(c => c.id !== id));
    if (currentConversationId === id) {
      const remaining = conversations.filter(c => c.id !== id);
      setCurrentConversationId(remaining.length > 0 ? remaining[0].id : null);
    }
  };

  const addMessage = (conversationId: string, message: Message) => {
    setConversations(prev => prev.map(conv => 
      conv.id === conversationId 
        ? { 
            ...conv, 
            messages: [...conv.messages, message],
            updatedAt: new Date()
          }
        : conv
    ));
  };

  const updateConversationTitle = (conversationId: string, title: string) => {
    setConversations(prev => prev.map(conv => 
      conv.id === conversationId 
        ? { 
            ...conv, 
            title: title.length > 30 ? title.substring(0, 30) + '...' : title,
            updatedAt: new Date()
          }
        : conv
    ));
  };

  return {
    conversations,
    currentConversation,
    currentConversationId,
    setCurrentConversationId,
    createNewConversation,
    deleteConversation,
    addMessage,
    updateConversationTitle
  };
};
