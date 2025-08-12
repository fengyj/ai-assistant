import React from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
}

/**
 * 通用模态框组件，负责展示弹窗内容和关闭逻辑
 */
const Modal: React.FC<ModalProps> = ({ isOpen, onClose, children, title }) => {
  if (!isOpen) return null;
  return (
    <div className="modal-overlay">
      <div className="modal-content w-full max-w-lg p-6">
        {title && <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">{title}</h2>}
        <button
          className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          onClick={onClose}
          aria-label="Close modal"
        >
          ×
        </button>
        {children}
      </div>
    </div>
  );
};

export default Modal;
