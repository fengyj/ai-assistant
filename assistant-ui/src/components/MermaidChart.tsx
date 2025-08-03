/*
 * MermaidChart.tsx
 * Standalone component for rendering Mermaid diagrams
 * Extracted from MarkdownRenderer for better separation of concerns
 */

import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { ClipboardDocumentIcon } from '@heroicons/react/24/outline';

interface MermaidChartProps {
  chart: string;
  theme: 'light' | 'dark';
}

const MermaidChart: React.FC<MermaidChartProps> = ({ chart, theme }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const prevChart = useRef<string>('');
  const prevTheme = useRef<'light' | 'dark'>('light');
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [showCode, setShowCode] = useState(false);

  useEffect(() => {
    // 仅在 chart 或 theme 变化时重新渲染
    if (prevChart.current === chart && prevTheme.current === theme) return;
    prevChart.current = chart;
    prevTheme.current = theme;
    const renderChart = async () => {
      if (!chartRef.current) return;
      try {
        setError(null);
        chartRef.current.innerHTML = '';
        // 根据 theme 自动切换 mermaid 主题
        mermaid.initialize({
          startOnLoad: false,
          theme: theme === 'dark' ? 'dark' : 'default',
          securityLevel: 'loose'
        });
        const id = `mermaid-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
        const { svg } = await mermaid.render(id, chart);
        if (chartRef.current) {
          chartRef.current.innerHTML = svg;
        }
      } catch (err) {
        console.error('Mermaid render error:', err);
        setError(err instanceof Error ? err.message : 'Render failed');
      }
    };
    renderChart();
  }, [chart, theme]);

  // 复制 mermaid 原始代码并显示反馈
  /**
   * 复制 mermaid 原始代码并显示反馈
   */
  const copyChart = () => {
    if (copied) return; // 防止重复点击
    navigator.clipboard.writeText(chart);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  if (error) {
    return (
      <div className="mermaid-wrapper my-6 md:my-8">
        {/* 错误头部区 */}
        <div className="mermaid-header bg-red-50 dark:bg-red-900 px-3 md:px-4 py-2 border border-red-300 dark:border-red-700 rounded-t-lg flex items-center justify-between">
          <span className="text-xs md:text-sm font-medium text-red-700 dark:text-red-300 uppercase tracking-wide">
            Mermaid (Render Failed)
          </span>
          <div className="flex items-center gap-2">
            <button
              className={`mermaid-copy-btn relative transition-all duration-200 px-2 py-1 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${copied ? 'opacity-60 cursor-not-allowed' : 'hover:bg-blue-100 dark:hover:bg-blue-900'}`}
              onClick={copyChart}
              title={copied ? '已复制' : '复制原始代码'}
              disabled={copied}
              aria-label="复制 mermaid 原始代码"
            >
              <ClipboardDocumentIcon className={`w-4 h-4 ${copied ? 'animate-pulse' : ''}`} />
              {copied && (
                <span className="absolute left-full ml-2 px-2 py-0.5 text-xs bg-green-500 text-white rounded shadow animate-fade-in">已复制</span>
              )}
            </button>
            <button
              className="ml-2 px-2 py-1 text-xs md:text-sm bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded hover:bg-gray-300 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              onClick={() => setShowCode((v) => !v)}
              aria-label={showCode ? '收起代码' : '展开原始代码'}
            >
              {showCode ? '收起代码' : '展开原始代码'}
            </button>
          </div>
        </div>
        {/* 错误信息区 */}
        <div className="bg-gray-50 dark:bg-gray-800 border border-red-300 dark:border-red-700 border-t-0 rounded-b-lg overflow-x-auto">
          <div className="p-3 md:p-4 text-sm md:text-base text-red-700 dark:text-red-300 font-semibold">
            {error}
          </div>
          {showCode && (
            <pre className="p-3 md:p-4 text-xs md:text-sm text-gray-800 dark:text-gray-200 overflow-x-auto whitespace-pre-wrap font-mono border-t border-gray-200 dark:border-gray-700">
              {chart}
            </pre>
          )}
        </div>
      </div>
    );
  }

  // 正常渲染区
  return (
    <div className="mermaid-wrapper my-6 md:my-8">
      {/* 图表头部区 */}
      <div className="mermaid-header bg-gray-100 dark:bg-gray-800 px-3 md:px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-t-lg flex items-center justify-between">
        <span className="text-xs md:text-sm font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">
          Mermaid Chart
        </span>
        <button
          className={`mermaid-copy-btn relative transition-all duration-200 px-2 py-1 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${copied ? 'opacity-60 cursor-not-allowed' : 'hover:bg-blue-100 dark:hover:bg-blue-900'}`}
          onClick={copyChart}
          title={copied ? '已复制' : '复制原始代码'}
          disabled={copied}
          aria-label="复制 mermaid 原始代码"
        >
          <ClipboardDocumentIcon className={`w-4 h-4 ${copied ? 'animate-pulse' : ''}`} />
          {copied && (
            <span className="absolute left-full ml-2 px-2 py-0.5 text-xs bg-green-500 text-white rounded shadow animate-fade-in">已复制</span>
          )}
        </button>
      </div>
      {/* Mermaid 渲染区 */}
      <div ref={chartRef} className="mermaid-chart bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-600 border-t-0 rounded-b-lg p-3 md:p-4 overflow-x-auto min-h-[200px]" />
    </div>
  );
};

export default MermaidChart;
