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
      <div className="chat-mermaid-wrapper">
        {/* 错误头部区 */}
        <div className="chat-mermaid-header chat-mermaid-header--error">
          <span className="chat-mermaid-title chat-mermaid-title--error">
            Mermaid (Render Failed)
          </span>
          <div className="flex items-center gap-2">
            <button
              className={`chat-mermaid-copy-btn ${copied ? 'chat-mermaid-copy-btn--disabled' : 'chat-mermaid-copy-btn--default'}`}
              onClick={copyChart}
              title={copied ? '已复制' : '复制原始代码'}
              disabled={copied}
              aria-label="复制 mermaid 原始代码"
            >
              <ClipboardDocumentIcon className={`w-4 h-4 ${copied ? 'animate-pulse' : ''}`} />
              {copied && (
                <span className="chat-mermaid-copy-feedback">已复制</span>
              )}
            </button>
            <button
              className="chat-mermaid-toggle-btn"
              onClick={() => setShowCode((v) => !v)}
              aria-label={showCode ? '收起代码' : '展开原始代码'}
            >
              {showCode ? '收起代码' : '展开原始代码'}
            </button>
          </div>
        </div>
        {/* 错误信息区 */}
        <div className="chat-mermaid-error-content">
          <div className="chat-mermaid-error-message">
            {error}
          </div>
          {showCode && (
            <pre className="chat-mermaid-source-code">
              {chart}
            </pre>
          )}
        </div>
      </div>
    );
  }

  // 正常渲染区
  return (
    <div className="chat-mermaid-wrapper">
      {/* 图表头部区 */}
      <div className="chat-mermaid-header chat-mermaid-header--success">
        <span className="chat-mermaid-title chat-mermaid-title--success">
          Mermaid Chart
        </span>
        <button
          className={`chat-mermaid-copy-btn ${copied ? 'chat-mermaid-copy-btn--disabled' : 'chat-mermaid-copy-btn--default'}`}
          onClick={copyChart}
          title={copied ? '已复制' : '复制原始代码'}
          disabled={copied}
          aria-label="复制 mermaid 原始代码"
        >
          <ClipboardDocumentIcon className={`w-4 h-4 ${copied ? 'animate-pulse' : ''}`} />
          {copied && (
            <span className="chat-mermaid-copy-feedback">已复制</span>
          )}
        </button>
      </div>
      {/* Mermaid 渲染区 */}
      <div ref={chartRef} className="chat-mermaid-chart" />
    </div>
  );
};

export default MermaidChart;
