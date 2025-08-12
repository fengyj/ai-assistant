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
            className="form-textarea-base"
            autoFocus
          />
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            按 Ctrl+Enter 保存，Esc 取消
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button
            onClick={onCancel}
            className="btn-modal-cancel"
          >
            取消
          </button>
          <button
            onClick={handleSave}
            disabled={!content.trim() || content === initialContent}
            className="btn-modal-save"
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
