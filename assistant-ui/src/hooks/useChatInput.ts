import { useState, useCallback, useRef } from 'react';

export interface UseChatInputReturn {
  // 输入状态
  inputValue: string;
  setInputValue: (value: string) => void;
  isComposing: boolean;
  
  // 文件状态
  files: File[];
  addFiles: (newFiles: File[]) => void;
  removeFile: (index: number) => void;
  clearFiles: () => void;
  
  // 输入框引用和方法
  textareaRef: React.RefObject<HTMLTextAreaElement | null>;
  adjustHeight: () => void;
  focusInput: () => void;
  
  // 发送相关
  canSend: boolean;
  handleSend: () => void;
  
  // 事件处理
  handleInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  handleKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  handleCompositionStart: () => void;
  handleCompositionEnd: () => void;
}

interface UseChatInputOptions {
  onSend: (content: string, files: File[]) => void;
  maxLength?: number;
  maxFiles?: number;
}

export const useChatInput = ({
  onSend,
  maxLength = 2000,
  maxFiles = 5,
}: UseChatInputOptions): UseChatInputReturn => {
  const [inputValue, setInputValue] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // 自动调整输入框高度
  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, []);

  // 聚焦输入框
  const focusInput = useCallback(() => {
    textareaRef.current?.focus();
  }, []);

  // 判断是否可以发送
  const canSend = inputValue.trim().length > 0 && inputValue.length <= maxLength;

  // 处理发送
  const handleSend = useCallback(() => {
    if (!canSend) return;
    
    onSend(inputValue.trim(), files);
    setInputValue('');
    setFiles([]);
    
    // 重置输入框高度
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }, 0);
  }, [canSend, inputValue, files, onSend]);

  // 处理输入变化
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      setInputValue(value);
      adjustHeight();
    }
  }, [maxLength, adjustHeight]);

  // 处理键盘事件
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl+Enter 或 Cmd+Enter 发送
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !isComposing) {
      e.preventDefault();
      handleSend();
    }
    // Shift+Enter 换行（默认行为）
    // 普通 Enter 在移动端发送，桌面端换行
    else if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      // 检测是否是移动设备
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
      if (isMobile) {
        e.preventDefault();
        handleSend();
      }
    }
  }, [isComposing, handleSend]);

  // 处理中文输入法
  const handleCompositionStart = useCallback(() => {
    setIsComposing(true);
  }, []);

  const handleCompositionEnd = useCallback(() => {
    setIsComposing(false);
  }, []);

  // 添加文件
  const addFiles = useCallback((newFiles: File[]) => {
    setFiles(prev => {
      const remainingSlots = maxFiles - prev.length;
      const filesToAdd = newFiles.slice(0, remainingSlots);
      return [...prev, ...filesToAdd];
    });
  }, [maxFiles]);

  // 移除文件
  const removeFile = useCallback((index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  }, []);

  // 清空文件
  const clearFiles = useCallback(() => {
    setFiles([]);
  }, []);

  return {
    inputValue,
    setInputValue,
    isComposing,
    files,
    addFiles,
    removeFile,
    clearFiles,
    textareaRef,
    adjustHeight,
    focusInput,
    canSend,
    handleSend,
    handleInputChange,
    handleKeyDown,
    handleCompositionStart,
    handleCompositionEnd,
  };
};
