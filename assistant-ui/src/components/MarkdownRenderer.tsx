/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useEffect, useRef, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vs, dark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { ClipboardDocumentIcon } from '@heroicons/react/24/outline';
import mermaid from 'mermaid';

interface MarkdownRendererProps {
  content: string;
  className?: string;
  theme?: 'light' | 'dark';
}

// 最基础的 Mermaid 图表组件
const MermaidChart: React.FC<{ 
  chart: string; 
  theme: 'light' | 'dark'; 
}> = ({ chart, theme }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    if (!chartRef.current) return;
    
    const renderChart = async () => {
      try {
        setError(null);
        
        // 清空容器
        if (chartRef.current) {
          chartRef.current.innerHTML = '';
        }
        
        // 初始化 Mermaid
        mermaid.initialize({
          startOnLoad: false,
          theme: 'neutral', // 使用中性主题，比 default 和 dark 更柔和
          securityLevel: 'loose'
        });
        
        // 生成唯一ID
        const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;
        
        // 渲染图表
        const { svg } = await mermaid.render(id, chart);
        
        // 插入到DOM
        if (chartRef.current) {
          chartRef.current.innerHTML = svg;
        }
        
      } catch (err) {
        console.error('Mermaid 渲染错误:', err);
        setError(err instanceof Error ? err.message : '渲染失败');
      }
    };
    
    renderChart();
  }, [chart, theme]);

  const copyChart = () => {
    navigator.clipboard.writeText(chart);
  };
  
  if (error) {
    return (
      <div className="mermaid-wrapper my-6">
        <div className="mermaid-header bg-gray-100 dark:bg-gray-800 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-t-lg flex items-center justify-between">
          <span className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">
            Mermaid (渲染失败)
          </span>
          <button
            className="mermaid-copy-btn"
            onClick={copyChart}
            title="复制图表代码"
          >
            <ClipboardDocumentIcon className="w-4 h-4" />
          </button>
        </div>
        <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-600 border-t-0 rounded-b-lg overflow-hidden">
          <pre className="p-4 text-sm text-gray-800 dark:text-gray-200 overflow-x-auto whitespace-pre-wrap font-mono">
            {chart}
          </pre>
        </div>
      </div>
    );
  }
  
  return (
    <div className="mermaid-wrapper my-6">
      <div className="mermaid-header bg-gray-100 dark:bg-gray-800 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-t-lg flex items-center justify-between">
        <span className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">
          Mermaid 图表
        </span>
        <button
          className="mermaid-copy-btn"
          onClick={copyChart}
          title="复制图表代码"
        >
          <ClipboardDocumentIcon className="w-4 h-4" />
        </button>
      </div>
      <div 
        ref={chartRef}
        className="mermaid-chart bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-600 border-t-0 rounded-b-lg p-4 overflow-x-auto min-h-[200px]"
      />
    </div>
  );
};

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
      
      // 处理 Mermaid 图表
      if (!inline && language === 'mermaid') {
        return (
          <MermaidChart 
            chart={String(children).replace(/\n$/, '')} 
            theme={theme} 
          />
        );
      }
      
      if (!inline && language) {
        return (
          <div className="code-block-wrapper my-4">
            <div className="code-block-header bg-gray-100 dark:bg-gray-800 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-t-lg flex items-center justify-between">
              <span className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">
                {language}
              </span>
              <button
                className="code-block-copy-btn"
                onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
                title="复制代码"
              >
                <ClipboardDocumentIcon className="w-4 h-4" />
              </button>
            </div>
            <SyntaxHighlighter
              style={theme === 'dark' ? dark : vs}
              language={language}
              PreTag="div"
              className="syntax-highlighter"
              showLineNumbers={false}
              wrapLines={true}
              customStyle={{
                margin: 0,
                borderRadius: '0 0 0.5rem 0.5rem',
                fontSize: '0.875rem',
                border: '1px solid',
                borderColor: theme === 'dark' ? '#374151' : '#e5e7eb',
                borderTop: 'none',
                backgroundColor: theme === 'dark' ? '#1f2937' : '#f9fafb',
                boxShadow: 'none', // 明确禁用阴影
              }}
              {...rest}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          </div>
        );
      }

      // 内联代码
      return (
        <code 
          className="bg-gray-100 dark:bg-gray-800 text-red-600 dark:text-red-400 px-1 py-0.5 rounded text-sm" 
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
