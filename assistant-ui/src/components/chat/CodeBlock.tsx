import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vs, vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
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
    <div className="code-block-wrapper">
      <div className="code-block-header">
        <span className="code-block-language">
          {language}
        </span>
        <button
          className="code-block-copy-btn"
          onClick={handleCopy}
          title={copied ? '已复制' : '复制代码'}
        >
          {/* 复制后图标变为√，否则显示原图标 */}
          {copied ? (
            <CheckIcon className="code-block-icon code-block-icon--copied" />
          ) : (
            <ClipboardDocumentIcon className="code-block-icon code-block-icon--default" />
          )}
        </button>
      </div>
      <SyntaxHighlighter
        style={theme === 'dark' ? vscDarkPlus : vs}
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
