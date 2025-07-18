import { type FC } from 'react';
import type { Message } from '../types';
import { MarkdownRenderer } from './MarkdownRenderer';
import { themeClasses } from '../utils/styles';

interface MessageComponentProps {
  message: Message;
}

export const MessageComponent: FC<MessageComponentProps> = ({ message }) => {
  const userMessageClasses = 'bg-blue-500 text-white';
  const assistantMessageClasses = `${themeClasses.bg.primary} ${themeClasses.text.primary} border ${themeClasses.border.primary}`;
  const timestampClasses = message.isUser 
    ? 'text-blue-100' 
    : themeClasses.text.muted;

  return (
    <div className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xl px-4 py-3 rounded-lg shadow-sm ${
        message.isUser ? userMessageClasses : assistantMessageClasses
      }`}>
        <MarkdownRenderer 
          content={message.content} 
          isUserMessage={message.isUser}
          className={message.isUser ? 'text-white' : themeClasses.text.primary}
        />
        <p className={`text-xs mt-2 ${timestampClasses}`}>
          {message.timestamp.toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
};

export default MessageComponent;