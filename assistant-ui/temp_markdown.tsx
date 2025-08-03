/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useEffect, useRef, useMemo, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vs, dark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { ClipboardDocumentIcon } from '@heroicons/react/24/outline';

interface MarkdownRendererProps {
  content: string;
  className?: string;
  theme?: 'light' | 'dark';
}

// Mermaid 图表组件 - 使用 iframe 完全隔离渲染
const MermaidChart: React.FC<{ 
  chart: string; 
  theme: 'light' | 'dark'; 
}> = React.memo(({ chart, theme }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [renderError, setRenderError] = React.useState<string | null>(null);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    setIsLoading(true);
    setRenderError(null);

    // 清理代码，移除可能有问题的语法
    const cleanedCode = chart.replace(/fa:fa-[\w-]+/g, '').trim();
    
    if (!cleanedCode || cleanedCode.length < 5) {
      setRenderError('无效的图表语法');
      setIsLoading(false);
      return;
    }

    // 创建 iframe 内容
    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@11.9.0/dist/mermaid.min.js"></script>
        <style>
          body {
            margin: 0;
            padding: 16px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: ${theme === 'dark' ? '#1f2937' : '#ffffff'};
            color: ${theme === 'dark' ? '#f9fafb' : '#111827'};
            overflow: hidden;
          }
          .mermaid {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: auto;
          }
          .error {
            color: ${theme === 'dark' ? '#fca5a5' : '#dc2626'};
            background: ${theme === 'dark' ? '#7f1d1d' : '#fef2f2'};
            border: 1px solid ${theme === 'dark' ? '#dc2626' : '#fca5a5'};
            border-radius: 8px;
            padding: 16px;
            font-size: 14px;
            max-width: 100%;
            word-wrap: break-word;
          }
          svg {
            max-width: 100%;
            height: auto;
          }
        </style>
      </head>
      <body>
        <div id="chart"></div>
        <script>
          (function() {
            try {
              // 初始化 Mermaid
              mermaid.initialize({
                startOnLoad: false,
                theme: '${theme === 'dark' ? 'dark' : 'default'}',
                securityLevel: 'strict',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                flowchart: {
                  useMaxWidth: true,
                  htmlLabels: false,
                },
                sequence: {
                  useMaxWidth: true,
                  wrap: true,
                },
                er: {
                  useMaxWidth: true,
                },
                suppressErrorRendering: true,
                logLevel: 'fatal'
              });

              const code = \`${cleanedCode.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`;
              const chartElement = document.getElementById('chart');
              
              // 设置渲染超时
              const timeout = setTimeout(() => {
                chartElement.innerHTML = '<div class="error">图表渲染超时</div>';
                window.parent.postMessage({ type: 'mermaid-error', error: '渲染超时' }, '*');
              }, 8000);

              // 渲染图表
              mermaid.render('chart-svg', code).then(function(result) {
                clearTimeout(timeout);
                if (result && result.svg) {
                  chartElement.innerHTML = result.svg;
                  // 调整 iframe 高度
                  const svgElement = chartElement.querySelector('svg');
                  if (svgElement) {
                    const height = svgElement.getBoundingClientRect().height + 32;
                    window.parent.postMessage({ 
                      type: 'mermaid-success', 
                      height: Math.max(100, height)
                    }, '*');
                  } else {
                    window.parent.postMessage({ type: 'mermaid-success', height: 200 }, '*');
                  }
                } else {
                  throw new Error('渲染结果为空');
                }
              }).catch(function(error) {
                clearTimeout(timeout);
                console.error('Mermaid error:', error);
                chartElement.innerHTML = '<div class="error">图表渲染失败: ' + (error.message || error) + '</div>';
                window.parent.postMessage({ 
                  type: 'mermaid-error', 
                  error: error.message || error.toString() 
                }, '*');
              });
            } catch (error) {
              console.error('Script error:', error);
              document.getElementById('chart').innerHTML = '<div class="error">图表初始化失败: ' + (error.message || error) + '</div>';
              window.parent.postMessage({ 
                type: 'mermaid-error', 
                error: error.message || error.toString() 
              }, '*');
            }
          })();
        </script>
      </body>
      </html>
    `;

    // 监听来自 iframe 的消息
    const messageHandler = (event: MessageEvent) => {
      if (event.source !== iframe.contentWindow) return;
      
      if (event.data.type === 'mermaid-success') {
        setIsLoading(false);
        setRenderError(null);
        // 动态调整 iframe 高度
        if (event.data.height) {
          iframe.style.height = `${event.data.height}px`;
        }
      } else if (event.data.type === 'mermaid-error') {
        setIsLoading(false);
        setRenderError(event.data.error || '渲染失败');
        iframe.style.height = '100px';
      }
    };

    window.addEventListener('message', messageHandler);

    // 写入 iframe 内容
    try {
      const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
      if (iframeDoc) {
        iframeDoc.open();
        iframeDoc.write(htmlContent);
        iframeDoc.close();
      } else {
        setRenderError('无法创建隔离环境');
        setIsLoading(false);
      }
    } catch (error) {
      console.error('iframe error:', error);
      setRenderError('iframe 创建失败');
      setIsLoading(false);
    }

    // 设置全局超时保护
    const globalTimeout = setTimeout(() => {
      if (isLoading) {
        setIsLoading(false);
        setRenderError('渲染超时');
      }
    }, 10000);

    return () => {
      window.removeEventListener('message', messageHandler);
      clearTimeout(globalTimeout);
    };
  }, [chart, theme]);

  const copyChart = useCallback(() => {
    navigator.clipboard.writeText(chart);
  }, [chart]);

  if (renderError) {
    return (
      <div className="mermaid-wrapper my-6">
        <div className="mermaid-header bg-gray-100 dark:bg-gray-800 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-t-lg flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Mermaid Chart</span>
          <button
            onClick={copyChart}
            className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 px-2 py-1 rounded border border-gray-300 dark:border-gray-600"
          >
            复制
          </button>
        </div>
        <div className="border border-red-300 dark:border-red-700 rounded-b-lg p-4 bg-red-50 dark:bg-red-950">
          <div className="text-red-700 dark:text-red-300 text-sm mb-2">图表渲染失败: {renderError}</div>
          <pre className="text-xs text-red-600 dark:text-red-400 overflow-auto whitespace-pre-wrap">{chart}</pre>
        </div>
      </div>
    );
  }

  return (
    <div className="mermaid-wrapper my-6">
      <div className="mermaid-header bg-gray-100 dark:bg-gray-800 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-t-lg flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Mermaid Chart</span>
        <button
          onClick={copyChart}
          className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 px-2 py-1 rounded border border-gray-300 dark:border-gray-600"
        >
          复制
        </button>
      </div>
      <div className="border border-gray-200 dark:border-gray-600 rounded-b-lg bg-white dark:bg-gray-900 relative overflow-hidden">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white dark:bg-gray-900 z-10">
            <div className="flex items-center text-gray-500 dark:text-gray-400">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500 mr-2"></div>
              正在渲染图表...
            </div>
          </div>
        )}
        <iframe
          ref={iframeRef}
          className="w-full border-none"
          style={{ 
            height: '200px',
            minHeight: '100px',
            visibility: isLoading ? 'hidden' : 'visible'
          }}
          sandbox="allow-scripts"
          title="Mermaid Chart"
        />
      </div>
    </div>
  );
}, (prevProps, nextProps) => {
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
