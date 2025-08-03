import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vs, dark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { ClipboardDocumentIcon } from '@heroicons/react/24/outline';

interface CodeBlockProps {
  language: string;
  value: string;
  theme: 'light' | 'dark';
  rest?: any;
}

/**
 * 代码块组件，带复制按钮和反馈
 */
const CodeBlock: React.FC<CodeBlockProps> = ({ language, value, theme, rest }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  return (
    <div className="code-block-wrapper my-4">
      <div className="code-block-header bg-gray-100 dark:bg-gray-800 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-t-lg flex items-center justify-between">
        <span className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">
          {language}
        </span>
        <button
          className="code-block-copy-btn relative"
          onClick={handleCopy}
          title={copied ? '已复制' : '复制代码'}
        >
          <ClipboardDocumentIcon className="w-4 h-4" />
          {copied && (
            <span className="absolute left-full ml-2 px-2 py-0.5 text-xs bg-green-500 text-white rounded shadow">已复制</span>
          )}
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
          boxShadow: 'none',
        }}
        {...rest}
      >
        {value}
      </SyntaxHighlighter>
    </div>
  );
};

export default CodeBlock;
