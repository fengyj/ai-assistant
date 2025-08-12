import React, { useState } from 'react';
import { XMarkIcon, CheckIcon } from '@heroicons/react/24/outline';

interface MessageEditModalProps {
  isOpen: boolean;
  initialContent: string;
  onSave: (newContent: string) => void;
  onCancel: () => void;
}

export const MessageEditModal: React.FC<MessageEditModalProps> = ({
  isOpen,
  initialContent,
  onSave,
  onCancel,
}) => {
  const [content, setContent] = useState(initialContent);

  if (!isOpen) return null;

  const handleSave = () => {
    if (content.trim() && content !== initialContent) {
      onSave(content.trim());
    } else {
      onCancel();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    } else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSave();
    }
  };

  return (
    <div className="modal-overlay p-4">
      <div className="modal-content w-full max-w-2xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            编辑消息
          </h3>
          <button
            onClick={onCancel}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 p-4">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="编辑消息内容..."
            className="w-full h-32 min-h-[128px] max-h-64 resize-y p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            autoFocus
          />
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            按 Ctrl+Enter 保存，Esc 取消
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-4 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500 rounded-lg transition-colors"
          >
            取消
          </button>
          <button
            onClick={handleSave}
            disabled={!content.trim() || content === initialContent}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-lg transition-colors flex items-center space-x-2"
          >
            <CheckIcon className="w-4 h-4" />
            <span>保存</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default MessageEditModal;
