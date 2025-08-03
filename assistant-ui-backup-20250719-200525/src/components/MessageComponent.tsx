import { type FC } from 'react';
import type { Message } from '../types';
import { MarkdownRenderer } from './MarkdownRenderer';


interface MessageComponentProps {
  message: Message;
}

export const MessageComponent: FC<MessageComponentProps> = ({ message }) => {
  const roleClass = message.isUser ? 'role-user' : 'role-assistant';

  return (
    <div className={`message-wrapper ${roleClass}`}>
      <div className={`message-bubble ${roleClass}`}>
        <MarkdownRenderer content={message.content} />
        <p className="timestamp">
          {message.timestamp.toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
};

export default MessageComponent;