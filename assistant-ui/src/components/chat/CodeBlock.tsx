import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vs, dark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { ClipboardDocumentIcon } from '@heroicons/react/24/outline';
import { CheckIcon } from '@heroicons/react/24/solid';

interface CodeBlockProps {
  language: string;
  value: string;
  theme: 'light' | 'dark';
  rest?: React.ComponentProps<typeof SyntaxHighlighter>;
}

/**
 * 代码块组件，带复制按钮和反馈
 */
const CodeBlock: React.FC<CodeBlockProps> = ({ language, value, theme, rest }) => {
  const [copied, setCopied] = useState(false);
  // 复制代码并切换按钮图标
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
          {/* 复制后图标变为√，否则显示原图标 */}
          {copied ? (
            <CheckIcon className="w-4 h-4 text-green-500 transition" />
          ) : (
            <ClipboardDocumentIcon className="w-4 h-4" />
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
        {...rest}
      >
        {value}
      </SyntaxHighlighter>
    </div>
  );
};

export default CodeBlock;
