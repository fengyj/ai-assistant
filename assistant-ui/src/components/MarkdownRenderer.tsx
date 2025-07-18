import { type FC, useMemo } from 'react';

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
  const renderedContent = useMemo(() => {
    const codeClass = isUserMessage 
      ? 'bg-blue-600/50 px-1 py-0.5 rounded-sm text-sm font-mono'
      : 'bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded-sm text-sm font-mono';
      
    const preClass = isUserMessage 
      ? 'bg-blue-600/50 p-3 rounded-lg mt-3 mb-3 overflow-x-auto'
      : 'bg-gray-100 dark:bg-gray-800 p-3 rounded-lg mt-3 mb-3 overflow-x-auto';
      
    const linkClass = isUserMessage 
      ? 'text-blue-200 hover:text-blue-100 underline'
      : 'text-blue-500 hover:text-blue-600 underline';

    const tableClass = isUserMessage
      ? 'min-w-full border-collapse border border-blue-300/50 mt-3 mb-3'
      : 'min-w-full border-collapse border border-gray-300 dark:border-gray-600 mt-3 mb-3';
      
    const thClass = isUserMessage
      ? 'border border-blue-300/50 px-3 py-2 bg-blue-600/30 font-semibold text-left'
      : 'border border-gray-300 dark:border-gray-600 px-3 py-2 bg-gray-100 dark:bg-gray-700 font-semibold text-left';
      
    const tdClass = isUserMessage
      ? 'border border-blue-300/50 px-3 py-2'
      : 'border border-gray-300 dark:border-gray-600 px-3 py-2';

    let result = content
      // Tables
      .replace(/\|(.+)\|\n\|[-:\s|]+\|\n((?:\|.+\|\n?)*)/g, (_, header, rows) => {
        const headerCells = header.split('|').map((cell: string) => cell.trim()).filter((cell: string) => cell);
        const headerRow = headerCells.map((cell: string) => `<th class="${thClass}">${cell}</th>`).join('');
        
        const bodyRows = rows.trim().split('\n').map((row: string) => {
          const cells = row.split('|').map((cell: string) => cell.trim()).filter((cell: string) => cell);
          return `<tr>${cells.map((cell: string) => `<td class="${tdClass}">${cell}</td>`).join('')}</tr>`;
        }).join('');
        
        return `<div class="overflow-x-auto"><table class="${tableClass}"><thead><tr>${headerRow}</tr></thead><tbody>${bodyRows}</tbody></table></div>`;
      })
      // Code blocks
      .replace(/```(\w+)?\n([\s\S]*?)```/g, `<pre class="${preClass}"><code class="text-sm font-mono">$2</code></pre>`)
      .replace(/```([\s\S]*?)```/g, `<pre class="${preClass}"><code class="text-sm font-mono">$1</code></pre>`)
      // Headers
      .replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>')
      .replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold mt-4 mb-2">$1</h2>')
      .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-4 mb-2">$1</h1>')
      // Lists
      .replace(/^- (.*$)/gm, '<li class="ml-4 list-disc leading-snug">$1</li>')
      .replace(/^\d+\. (.*$)/gm, '<li class="ml-4 list-decimal leading-snug">$1</li>')
      // Bold and italic
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      // Inline code
      .replace(/`([^`]+)`/g, `<code class="${codeClass}">$1</code>`)
      // Links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, `<a href="$2" class="${linkClass}" target="_blank" rel="noopener noreferrer">$1</a>`);

    // Handle paragraphs and line breaks
    result = result
      .split(/\n\s*\n/)
      .map(paragraph => paragraph.trim())
      .filter(paragraph => paragraph.length > 0)
      .map(paragraph => {
        if (paragraph.match(/^<(h[1-6]|li|pre|div)/)) {
          return paragraph;
        }
        return `<p class="mb-3">${paragraph.replace(/\n/g, '<br />')}</p>`;
      })
      .join('');

    // Clean up list formatting
    result = result
      .replace(/(<\/li>)\s*<br\s*\/?>\s*(<li)/g, '$1$2')
      .replace(/(<\/li>)\s*(<li)/g, '$1$2');

    return result;
  }, [content, isUserMessage]);

  return (
    <div 
      className={`prose prose-sm max-w-none ${className}`}
      dangerouslySetInnerHTML={{ __html: renderedContent }}
    />
  );
};

export default MarkdownRenderer;