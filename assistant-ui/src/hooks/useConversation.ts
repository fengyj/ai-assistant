import { useContext } from 'react';
import { ConversationContext } from '../context/ConversationContext';
import type { ConversationContextType } from '../context/ConversationContext';

export const useConversation = (): ConversationContextType => {
  const context = useContext(ConversationContext);
  
  if (!context) {
    throw new Error('useConversation must be used within a ConversationProvider');
  }
  
  return context;
};
