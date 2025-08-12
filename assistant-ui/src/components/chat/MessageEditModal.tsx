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
        <div className="modal-header">
          <h3 className="modal-title">
            编辑消息
          </h3>
          <button
            onClick={onCancel}
            className="modal-close-btn"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="modal-body">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="编辑消息内容..."
            className="form-textarea-base"
            autoFocus
          />
          <div className="modal-help-text">
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
