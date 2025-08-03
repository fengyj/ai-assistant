/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useEffect, useRef, useMemo, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow, dark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import mermaid from 'mermaid';

interface MarkdownRendererProps {
  content: string;
  className?: string;
  theme?: 'light' | 'dark';
}

// 创建一个全局缓存来存储已渲染的 Mermaid 图表
const mermaidCache = new Map<string, string>();

// 生成稳定的图表ID，基于内容的哈希
const generateStableId = (content: string): string => {
  let hash = 0;
  for (let i = 0; i < content.length; i++) {
    const char = content.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // 转换为32位整数
  }
  return `mermaid-${Math.abs(hash).toString(36)}`;
};

// Mermaid 图表组件
const MermaidChart: React.FC<{ 
  chart: string; 
  theme: 'light' | 'dark'; 
}> = React.memo(({ chart, theme }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [renderError, setRenderError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  
  // 生成稳定的图表ID
  const chartId = useMemo(() => generateStableId(chart), [chart]);
  const cacheKey = useMemo(() => `${chartId}-${theme}`, [chartId, theme]);
  
  // 检查缓存
  const cachedSvg = mermaidCache.get(cacheKey);
  
  const renderMermaid = useCallback(async () => {
    if (!chartRef.current) return;
    
    // 使用 try-catch 包装整个渲染过程
    try {
      setIsLoading(true);
      setRenderError(null);
      
      // 如果有缓存，直接使用
      if (cachedSvg) {
        try {
          chartRef.current.innerHTML = cachedSvg;
          setIsLoading(false);
          return;
        } catch (cacheError) {
          console.warn('Cache error, will re-render:', cacheError);
          // 清除有问题的缓存
          mermaidCache.delete(cacheKey);
        }
      }
      
      // 清理图表内容，移除可能导致问题的语法
      let cleanChart = chart.trim();
      if (!cleanChart) {
        throw new Error('图表内容为空');
      }
      
      // 移除或替换不支持的 Font Awesome 语法
      cleanChart = cleanChart.replace(/fa:fa-(\w+)/g, '$1');
      
      // 验证基本的 Mermaid 语法
      if (!cleanChart.includes('graph') && 
          !cleanChart.includes('flowchart') && 
          !cleanChart.includes('sequenceDiagram') && 
          !cleanChart.includes('classDiagram') && 
          !cleanChart.includes('stateDiagram') &&
          !cleanChart.includes('gitgraph') &&
          !cleanChart.includes('pie') &&
          !cleanChart.includes('journey') &&
          !cleanChart.includes('gantt') &&
          !cleanChart.includes('erDiagram') &&
          !cleanChart.includes('mindmap')) {
        throw new Error('不支持的图表类型或语法错误');
      }
      
      // 配置 Mermaid 主题 - 使用更安全的配置
      try {
        mermaid.initialize({
          startOnLoad: false,
          theme: theme === 'dark' ? 'dark' : 'default',
          securityLevel: 'strict', // 改为 strict 提高安全性
          fontFamily: 'Arial, sans-serif',
          suppressErrorRendering: false,
          logLevel: 'error',
          themeVariables: {
            primaryColor: '#3b82f6',
            primaryTextColor: theme === 'dark' ? '#f3f4f6' : '#1f2937',
            primaryBorderColor: '#6b7280',
            lineColor: '#6b7280',
            secondaryColor: '#e5e7eb',
            tertiaryColor: '#f3f4f6',
            background: theme === 'dark' ? '#1f2937' : '#ffffff',
            mainBkg: theme === 'dark' ? '#374151' : '#f9fafb',
            secondBkg: theme === 'dark' ? '#4b5563' : '#e5e7eb',
          }
        });
      } catch (initError) {
        console.error('Mermaid initialization error:', initError);
        throw new Error(`Mermaid 初始化失败: ${initError instanceof Error ? initError.message : '未知错误'}`);
      }

      // 渲染图表 - 添加超时保护
      const renderPromise = mermaid.render(chartId, cleanChart);
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('渲染超时')), 10000); // 10秒超时
      });
      
      const result = await Promise.race([renderPromise, timeoutPromise]) as { svg: string };
      
      if (chartRef.current && result && result.svg) {
        chartRef.current.innerHTML = result.svg;
        // 缓存渲染结果
        mermaidCache.set(cacheKey, result.svg);
        setIsLoading(false);
      } else {
        throw new Error('渲染结果为空');
      }
      
    } catch (error) {
      console.error('Mermaid rendering error:', error);
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      setRenderError(errorMessage);
      setIsLoading(false);
      
      // 确保即使出错也清空内容，避免显示损坏的 SVG
      if (chartRef.current) {
        chartRef.current.innerHTML = '';
      }
      
      // 清除可能有问题的缓存
      mermaidCache.delete(cacheKey);
    }
  }, [chart, theme, chartId, cacheKey, cachedSvg]);

  useEffect(() => {
    // 避免在组件销毁时渲染
    let isMounted = true;
    
    const render = async () => {
      if (isMounted && chartRef.current) {
        try {
          await renderMermaid();
        } catch (error) {
          console.error('Effect render error:', error);
          if (isMounted) {
            setRenderError(error instanceof Error ? error.message : '渲染失败');
            setIsLoading(false);
          }
        }
      }
    };
    
    render();
    
    return () => {
      isMounted = false;
    };
  }, [renderMermaid]);

  const copyChart = useCallback(() => {
    navigator.clipboard.writeText(chart);
  }, [chart]);

  return (
    <div className="mermaid-wrapper my-6">
      <div className="mermaid-header bg-gray-100 dark:bg-gray-800 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-t-lg flex items-center justify-between">
        <span className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">
          Mermaid 图表
        </span>
        <button
          className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors px-2 py-1 rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"
          onClick={copyChart}
          title="复制图表代码"
        >
          复制
        </button>
      </div>
      <div 
        ref={chartRef}
        className="mermaid-chart bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-600 border-t-0 rounded-b-lg p-4 overflow-x-auto min-h-[200px] flex items-center justify-center"
      >
        {isLoading && !cachedSvg && (
          <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span className="text-sm">正在渲染图表...</span>
          </div>
        )}
        {renderError && (
          <div className="w-full p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-800 dark:text-red-200 text-sm">
              图表渲染失败: {renderError}
            </p>
            <pre className="mt-2 text-xs text-red-700 dark:text-red-300 overflow-x-auto">
              {chart}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}, (prevProps, nextProps) => {
  // 自定义比较函数，只在内容或主题真正改变时重新渲染
  return prevProps.chart === nextProps.chart && prevProps.theme === nextProps.theme;
});

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
                className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors px-2 py-1 rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"
                onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
                title="复制代码"
              >
                复制
              </button>
            </div>
            <SyntaxHighlighter
              style={theme === 'dark' ? dark : tomorrow}
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
              }}
              {...rest}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          </div>
        );
      }
      
      // 行内代码
      return (
        <code 
          className="inline-code bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 px-1.5 py-0.5 rounded text-sm font-mono"
          {...rest}
        >
          {children}
        </code>
      );
    },
    
    // 段落组件
    p: ({ children }: any) => (
      <p className="mb-3 last:mb-0 leading-relaxed">
        {children}
      </p>
    ),
    
    // 标题组件
    h1: ({ children }: any) => (
      <h1 className="text-2xl font-bold mb-4 mt-6 first:mt-0 text-gray-900 dark:text-gray-100">
        {children}
      </h1>
    ),
    h2: ({ children }: any) => (
      <h2 className="text-xl font-bold mb-3 mt-5 first:mt-0 text-gray-900 dark:text-gray-100">
        {children}
      </h2>
    ),
    h3: ({ children }: any) => (
      <h3 className="text-lg font-semibold mb-2 mt-4 first:mt-0 text-gray-900 dark:text-gray-100">
        {children}
      </h3>
    ),
    h4: ({ children }: any) => (
      <h4 className="text-base font-semibold mb-2 mt-3 first:mt-0 text-gray-900 dark:text-gray-100">
        {children}
      </h4>
    ),
    h5: ({ children }: any) => (
      <h5 className="text-sm font-semibold mb-2 mt-3 first:mt-0 text-gray-900 dark:text-gray-100">
        {children}
      </h5>
    ),
    h6: ({ children }: any) => (
      <h6 className="text-xs font-semibold mb-2 mt-3 first:mt-0 text-gray-900 dark:text-gray-100">
        {children}
      </h6>
    ),
    
    // 列表组件
    ul: ({ children }: any) => (
      <ul className="list-disc pl-6 mb-3 space-y-1">
        {children}
      </ul>
    ),
    ol: ({ children }: any) => (
      <ol className="list-decimal pl-6 mb-3 space-y-1">
        {children}
      </ol>
    ),
    li: ({ children }: any) => (
      <li className="text-gray-900 dark:text-gray-100">
        {children}
      </li>
    ),
    
    // 引用组件
    blockquote: ({ children }: any) => (
      <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 py-2 my-4 bg-gray-50 dark:bg-gray-800 italic text-gray-700 dark:text-gray-300">
        {children}
      </blockquote>
    ),
    
    // 链接组件
    a: ({ children, href, ...props }: any) => (
      <a
        href={href}
        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline decoration-1 underline-offset-2 hover:decoration-2 transition-all duration-200"
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    ),
    
    // 图像组件
    img: ({ src, alt, title, ...props }: any) => (
      <div className="image-wrapper my-4">
        <img
          src={src}
          alt={alt || ''}
          title={title}
          className="max-w-full h-auto rounded-lg border border-gray-200 dark:border-gray-600 shadow-sm hover:shadow-md transition-shadow duration-200"
          loading="lazy"
          {...props}
        />
        {alt && (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center mt-2 italic">
            {alt}
          </p>
        )}
      </div>
    ),
    
    // 水平分割线
    hr: () => (
      <hr className="my-6 border-gray-300 dark:border-gray-600" />
    ),
    
    // 表格组件
    table: ({ children }: any) => (
      <div className="table-wrapper overflow-x-auto my-6 rounded-lg border border-gray-200 dark:border-gray-600 shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
          {children}
        </table>
      </div>
    ),
    thead: ({ children }: any) => (
      <thead className="bg-gray-50 dark:bg-gray-800">
        {children}
      </thead>
    ),
    tbody: ({ children }: any) => (
      <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
        {children}
      </tbody>
    ),
    tr: ({ children }: any) => (
      <tr className="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-150">
        {children}
      </tr>
    ),
    th: ({ children }: any) => (
      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider bg-gray-50 dark:bg-gray-800">
        {children}
      </th>
    ),
    td: ({ children }: any) => (
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
        {children}
      </td>
    ),
    
    // 强调文本
    strong: ({ children }: any) => (
      <strong className="font-semibold text-gray-900 dark:text-gray-100">
        {children}
      </strong>
    ),
    em: ({ children }: any) => (
      <em className="italic text-gray-900 dark:text-gray-100">
        {children}
      </em>
    ),
  }), [theme]); // 只在主题改变时重新创建组件配置

  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}, (prevProps, nextProps) => {
  // 自定义比较函数，只在内容或主题真正改变时重新渲染
  return prevProps.content === nextProps.content && 
         prevProps.theme === nextProps.theme && 
         prevProps.className === nextProps.className;
});
