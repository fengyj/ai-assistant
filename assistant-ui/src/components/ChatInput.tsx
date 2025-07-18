import { type FC, useRef, useEffect } from 'react';

interface ChatInputProps {
  message: string;
  selectedFiles: File[];
  isLoading: boolean;
  isDarkMode: boolean;
  isDragOver: boolean;
  onMessageChange: (value: string) => void;
  onFileSelect: (files: File[]) => void;
  onRemoveFile: (index: number) => void;
  onSendMessage: () => void;
  onCancelRequest: () => void;
  onCreateNewConversation: () => void;
  onDragOver: (e: React.DragEvent) => void;
  onDragLeave: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent) => void;
  getFileIcon: (file: File) => string;
}

export const ChatInput: FC<ChatInputProps> = ({
  message,
  selectedFiles,
  isLoading,
  isDarkMode,
  isDragOver,
  onMessageChange,
  onFileSelect,
  onRemoveFile,
  onSendMessage,
  onCancelRequest,
  onCreateNewConversation,
  onDragOver,
  onDragLeave,
  onDrop,
  getFileIcon
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustTextareaHeight = (element: HTMLTextAreaElement) => {
    element.style.height = 'auto';
    element.style.height = Math.min(element.scrollHeight, 200) + 'px';
  };

  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onMessageChange(e.target.value);
    adjustTextareaHeight(e.target);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    onFileSelect(files);
    e.target.value = '';
  };

  useEffect(() => {
    if (textareaRef.current && !isLoading) {
      textareaRef.current.focus();
    }
  }, [isLoading]);

  return (
    <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-t p-4`}>
      <div className="max-w-4xl mx-auto">
        <div 
          className={`border rounded-lg ${
            isDarkMode ? 'border-gray-600 bg-gray-800' : 'border-gray-300 bg-white'
          } ${isDragOver ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20' : ''} transition-colors`}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
        >
          {/* 文件上传区域 */}
          <div className={`px-4 py-0.5 ${
            selectedFiles.length > 0 || isDragOver ? 'border-b' : ''
          } ${isDarkMode ? 'border-gray-600' : 'border-gray-200'}`}>
            <div className="flex items-center flex-wrap gap-x-1 gap-y-0.5">
              {/* 文件上传按钮 */}
              <div className="relative">
                <input
                  type="file"
                  multiple
                  onChange={handleFileInputChange}
                  className="hidden"
                  id="file-upload"
                  accept="image/*,.pdf,.doc,.docx,.txt,.csv,.xlsx,.xls"
                />
                <label
                  htmlFor="file-upload"
                  className={`inline-flex items-center px-2 py-1 rounded cursor-pointer transition-colors ${
                    isDarkMode 
                      ? 'text-gray-400 hover:text-gray-300 hover:bg-gray-700' 
                      : 'text-gray-600 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                  title="添加文件"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66L9.64 16.2a2 2 0 11-2.83-2.83l8.49-8.49" />
                  </svg>
                </label>
              </div>

              {/* 文件列表 */}
              {selectedFiles.map((file, index) => (
                <div 
                  key={index}
                  className={`flex items-center gap-x-0.5 px-2 py-1 rounded text-xs transition-colors ${
                    isDarkMode 
                      ? 'text-gray-300 hover:bg-gray-700' 
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <span className="text-xs">{getFileIcon(file)}</span>
                  <span className="font-medium truncate max-w-[80px]" title={file.name}>
                    {file.name}
                  </span>
                  <span className={`text-[9px] ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                    ({(file.size / 1024).toFixed(0)}K)
                  </span>
                  <button
                    onClick={() => onRemoveFile(index)}
                    className={`p-0.5 rounded text-red-500 hover:text-red-600 transition-colors ${
                      isDarkMode 
                        ? 'hover:bg-red-900/20' 
                        : 'hover:bg-red-50'
                    }`}
                    title="移除文件"
                  >
                    <svg className="w-2 h-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>

            {/* 拖拽提示 */}
            {isDragOver && (
              <div className={`mt-2 p-3 border-2 border-dashed rounded-lg text-center ${
                isDarkMode 
                  ? 'border-blue-400 bg-blue-900/20 text-blue-300' 
                  : 'border-blue-400 bg-blue-50 text-blue-600'
              }`}>
                <svg className="w-5 h-5 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-xs font-medium">拖拽文件到此处上传</p>
                <p className="text-[10px] mt-0.5">支持图片、文档等多种格式，最大10MB</p>
              </div>
            )}
          </div>
          
          {/* 输入和按钮区域 */}
          <div className="px-4 py-3">
            <div className="flex items-end space-x-3">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={handleMessageChange}
                onKeyDown={handleKeyDown}
                placeholder="输入消息... (Ctrl+Enter 发送)"
                rows={1}
                className={`flex-1 px-0 py-2 resize-none min-h-8 max-h-[200px] overflow-y-auto border-none outline-none ${
                  isDarkMode 
                    ? 'bg-transparent text-white placeholder-gray-400' 
                    : 'bg-transparent text-gray-900 placeholder-gray-500'
                }`}
                disabled={isLoading}
              />
              
              {/* 发送/取消按钮 */}
              <button
                onClick={isLoading ? onCancelRequest : onSendMessage}
                disabled={!isLoading && (!message.trim() && selectedFiles.length === 0)}
                className={`p-2 rounded-md transition-colors ${
                  !isLoading && (!message.trim() && selectedFiles.length === 0)
                    ? isDarkMode ? 'text-gray-600' : 'text-gray-400'
                    : isLoading
                      ? isDarkMode 
                        ? 'text-red-400 hover:text-red-300 hover:bg-gray-700' 
                        : 'text-red-600 hover:text-red-700 hover:bg-gray-100'
                      : isDarkMode 
                        ? 'text-blue-400 hover:text-blue-300 hover:bg-gray-700' 
                        : 'text-blue-600 hover:text-blue-700 hover:bg-gray-100'
                }`}
                title={isLoading ? "取消生成" : "发送消息"}
              >
                {isLoading ? (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <rect x="6" y="6" width="12" height="12" rx="2" ry="2"/>
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                  </svg>
                )}
              </button>
              
              {/* 新对话按钮 */}
              <button
                onClick={onCreateNewConversation}
                className={`p-2 rounded-md transition-colors ${
                  isDarkMode 
                    ? 'text-gray-400 hover:text-white hover:bg-gray-700' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
                title="新建对话"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        {/* 使用提示 */}
        <p className={`text-xs mt-2 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          支持拖拽文件上传 • 按 Enter 换行，按 Ctrl+Enter 发送消息 • 按 Ctrl+V 粘贴截图/文件
        </p>
      </div>
    </div>
  );
};

export default ChatInput;
