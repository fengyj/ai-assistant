// conversationUtils.ts
// Utility functions for conversation and message operations
// All business logic for message creation, editing, deletion, AI simulation, etc. should be placed here.

import type { Conversation, Message } from '../types';

/**
 * Create a new conversation object
 */
export function createConversationObject(id: string, title: string): Conversation {
  return {
    id,
    title,
    messages: [],
    createdAt: new Date(),
    updatedAt: new Date(),
  };
}

/**
 * Create a new user message
 */
export function createUserMessage(id: string, content: string, conversationId: string, files?: File[]): Message {
  return {
    id,
    content,
    role: 'user',
    timestamp: new Date(),
    conversationId,
    metadata: files && files.length > 0 ? {
      files: files.map(file => ({
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`,
        name: file.name,
        size: file.size,
        type: file.type,
      }))
    } : undefined
  };
}

/**
 * Create a new AI message (simulated)
 */
export function createAIMessage(id: string, content: string, conversationId: string, tokens = 50, regenerated = false): Message {
  return {
    id,
    content,
    role: 'assistant',
    timestamp: new Date(),
    conversationId,
    metadata: {
      model: 'GPT-4',
      tokens,
      ...(regenerated ? { regenerated: true } : {})
    }
  };
}

/**
 * Edit a message in a conversation
 */
export function editMessage(messages: Message[], messageId: string, newContent: string): Message[] {
  return messages.map(msg =>
    msg.id === messageId ? { ...msg, content: newContent } : msg
  );
}

/**
 * Delete a message from a conversation
 */
export function deleteMessage(messages: Message[], messageId: string): Message[] {
  return messages.filter(msg => msg.id !== messageId);
}
