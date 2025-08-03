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
    <span className="relative group">
      {children}
      <span className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2 py-1 text-xs bg-gray-800 text-white rounded opacity-0 group-hover:opacity-100 transition pointer-events-none whitespace-nowrap z-10">
        {content}
      </span>
    </span>
  );
};

export default Tooltip;
