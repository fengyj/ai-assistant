/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import MermaidChart from './MermaidChart';
import CodeBlock from './CodeBlock';

interface MarkdownRendererProps {
  content: string;
  className?: string;
  theme?: 'light' | 'dark';
}



export const MarkdownRenderer: React.FC<MarkdownRendererProps> = React.memo(({ 
  content, 
  className = '', 
  theme = 'light' 
}) => {
  // 使用 useMemo 缓存组件配置，避免每次重新创建
  const components = useMemo(() => ({
    // 代码块组件
    code: (props: any) => {
      const { inline, className, children, ...rest } = props;
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';

      // Mermaid 图表渲染，异常时友好提示
      if (!inline && language === 'mermaid') {
        // MermaidChart 需在内部处理错误，若渲染失败则显示错误提示
        return (
          <MermaidChart 
            chart={String(children).replace(/\n$/, '')} 
            theme={theme}
          />
        );
      }

      // 代码块使用独立组件
      if (!inline && language) {
        return (
          <CodeBlock
            language={language}
            value={String(children).replace(/\n$/, '')}
            theme={theme}
            rest={rest}
          />
        );
      }

      // 内联代码样式微调，提升可读性
      return (
        <code 
          className="bg-gray-100 dark:bg-gray-800 text-pink-700 dark:text-pink-400 px-1.5 py-0.5 rounded text-[0.95em] font-mono border border-gray-200 dark:border-gray-700" 
          {...rest}
        >
          {children}
        </code>
      );
    },

    // 表格组件
    table: (props: any) => (
      <div className="overflow-x-auto my-4">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700" {...props} />
      </div>
    ),
    thead: (props: any) => (
      <thead className="bg-gray-50 dark:bg-gray-800" {...props} />
    ),
    tbody: (props: any) => (
      <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700" {...props} />
    ),
    tr: (props: any) => (
      <tr className="hover:bg-gray-50 dark:hover:bg-gray-800" {...props} />
    ),
    th: (props: any) => (
      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider" {...props} />
    ),
    td: (props: any) => (
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100" {...props} />
    ),

    // 图片组件
    img: (props: any) => (
      <div className="my-4">
        <img 
          className="max-w-full h-auto rounded-lg shadow-sm" 
          loading="lazy"
          {...props} 
        />
        {props.alt && (
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 text-center italic">
            {props.alt}
          </p>
        )}
      </div>
    ),

    // 链接组件
    a: (props: any) => (
      <a 
        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline" 
        target="_blank" 
        rel="noopener noreferrer" 
        {...props} 
      />
    ),

    // 引用块
    blockquote: (props: any) => (
      <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 py-2 my-4 italic text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 rounded-r-lg" {...props} />
    ),

    // 标题组件
    h1: (props: any) => (
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-8 mb-4 border-b border-gray-200 dark:border-gray-700 pb-2" {...props} />
    ),
    h2: (props: any) => (
      <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mt-6 mb-3 border-b border-gray-200 dark:border-gray-700 pb-2" {...props} />
    ),
    h3: (props: any) => (
      <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mt-5 mb-3" {...props} />
    ),
    h4: (props: any) => (
      <h4 className="text-lg font-medium text-gray-900 dark:text-gray-100 mt-4 mb-2" {...props} />
    ),
    h5: (props: any) => (
      <h5 className="text-base font-medium text-gray-900 dark:text-gray-100 mt-3 mb-2" {...props} />
    ),
    h6: (props: any) => (
      <h6 className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-3 mb-2" {...props} />
    ),

    // 列表组件
    ul: (props: any) => (
      <ul className="list-disc list-inside my-4 space-y-1 text-gray-700 dark:text-gray-300" {...props} />
    ),
    ol: (props: any) => (
      <ol className="list-decimal list-inside my-4 space-y-1 text-gray-700 dark:text-gray-300" {...props} />
    ),
    li: (props: any) => (
      <li className="leading-relaxed" {...props} />
    ),

    // 段落
    p: (props: any) => (
      <p className="my-3 leading-relaxed text-gray-700 dark:text-gray-300" {...props} />
    ),

    // 分隔线
    hr: (props: any) => (
      <hr className="my-6 border-gray-300 dark:border-gray-600" {...props} />
    ),

    // 强调
    strong: (props: any) => (
      <strong className="font-semibold text-gray-900 dark:text-gray-100" {...props} />
    ),
    em: (props: any) => (
      <em className="italic text-gray-700 dark:text-gray-300" {...props} />
    ),
  }), [theme]);

  return (
    <div className={`markdown-renderer prose prose-gray dark:prose-invert max-w-none ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
});

MarkdownRenderer.displayName = 'MarkdownRenderer';
