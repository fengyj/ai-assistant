import React from 'react';

interface TooltipProps {
  content: string;
  children: React.ReactNode;
}

/**
 * 通用 Tooltip 组件，负责悬停提示内容展示
 */
const Tooltip: React.FC<TooltipProps> = ({ content, children }) => {
  return (
    <span className="tooltip-trigger">
      {children}
      <span className="tooltip-content">
        {content}
      </span>
    </span>
  );
};

export default Tooltip;
