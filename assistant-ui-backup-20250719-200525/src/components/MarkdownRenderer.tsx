import { type FC } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content: string;
  className?: string;
  isUserMessage?: boolean;
}

export const MarkdownRenderer: FC<MarkdownRendererProps> = ({ 
  content, 
  className = '',
  isUserMessage = false 
}) => {
  // 只在顶层加 .user 或 .ai-assistant class，子元素用标准标签
  const topClass = isUserMessage ? 'user' : 'ai-assistant';
  return (
    <div className={`prose prose-sm max-w-none ${className} ${topClass}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;