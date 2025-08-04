import React, { useEffect, useRef } from 'react';
import { useEditingMessage } from '../../hooks/useEditingMessage';
import { Button } from '../ui/Button';
import { MarkdownRenderer } from '../MarkdownRenderer';
import { useSidebar } from '../../hooks/useSidebar';
import { useConversation } from '../../hooks/useConversation';
import { useChatInput } from '../../hooks/useChatInput';
import { useMessageActions } from '../../hooks/useMessageActions';
import { FileUpload } from './FileUpload';
import { MessageEditModal } from './MessageEditModal';
import { 
  SunIcon, 
  MoonIcon, 
  PaperAirplaneIcon,
  StopIcon,
  MicrophoneIcon,
  PlusIcon,
  CogIcon,
  ClipboardDocumentIcon,
  PencilIcon,
  ArrowPathIcon,
  HandThumbUpIcon,
  HandThumbDownIcon,
  InformationCircleIcon,
  Bars3Icon
} from '@heroicons/react/24/outline';
import { CheckIcon } from '@heroicons/react/24/solid';

interface ChatAreaProps {
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({ theme, onToggleTheme }) => {
  const { toggleMobileOpen } = useSidebar();
  const { currentConversation, sendMessage, cancelResponse, isLoading } = useConversation();
  
  // 编辑模态框状态
  // Use custom hook for editing message state
  const { editingMessage, setEditingMessage } = useEditingMessage<{ id: string; content: string }>();
  
  // 滚动相关refs
  const messageContainerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // 消息操作Hook
  const {
    copyMessage,
    editMessage,
    regenerateMessage,
    likeMessage,
    dislikeMessage,
    isProcessing,
    copiedMessageId,
  } = useMessageActions();
  
  // 使用聊天输入 Hook
  const {
    inputValue,
    files,
    textareaRef,
    canSend,
    isSending,
    handleSend,
    handleCancel,
    resetSending,
    handleInputChange,
    handleKeyDown,
    handleCompositionStart,
    handleCompositionEnd,
    handleFilesChange,
    handlePaste,
  } = useChatInput({
    onSend: sendMessage,
    onCancel: cancelResponse,
  });

  // 获取当前对话的消息，如果没有对话则显示空数组
  const messages = currentConversation?.messages || [];

  // 滚动到底部函数
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'end'
    });
  };

  // 监听消息变化，自动滚动到底部
  useEffect(() => {
    // 延迟滚动，确保DOM已更新
    const timeoutId = setTimeout(() => {
      scrollToBottom();
    }, 100);

    return () => clearTimeout(timeoutId);
  }, [messages.length, isLoading]);

  // 同步发送状态：当 isLoading 变为 false 时，重置发送状态
  useEffect(() => {
    if (!isLoading && isSending) {
      resetSending();
    }
  }, [isLoading, isSending, resetSending]);

  // 处理编辑消息
  const handleEditSave = async (newContent: string) => {
    if (editingMessage) {
      await editMessage(editingMessage.id, newContent);
      setEditingMessage(null);
    }
  };

  const handleEditCancel = () => {
    setEditingMessage(null);
  };

  // 主题切换由全局 <html> 或 <body> 的 class 控制，不在此处加 dark/light class
  return (
    <div className="flex flex-col h-full"> 
      {/* 顶部：对话标题栏 */}
      <div className="chat-header">
        {/* 移动端菜单按钮 */}
        <Button 
          variant="icon" 
          onClick={toggleMobileOpen}
          className="md:hidden mr-2"
        >
          <Bars3Icon className="w-5 h-5" />
        </Button>
        
        <h1 className="chat-title">
          关于React Hook的问题
        </h1>
        <Button variant="icon" onClick={onToggleTheme}>
          {theme === 'light' ? (
            <MoonIcon className="w-5 h-5" />
          ) : (
            <SunIcon className="w-5 h-5" />
          )}
        </Button>
      </div>

      {/* 中间：消息列表 */}
      <div className="message-container" ref={messageContainerRef}>
        <div className="message-wrapper">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
            >
              <div
                className={`group ${
                  message.role === 'user'
                    ? 'message-bubble message-bubble-user'
                    : 'message-bubble message-bubble-ai'
                }`}
              >
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  {message.metadata?.regenerated && (
                    <div className="mb-2 text-xs text-orange-600 dark:text-orange-400 font-medium">
                      🔄 重新生成的回复
                    </div>
                  )}
                  <MarkdownRenderer 
                    content={message.content} 
                    theme={theme}
                    className={message.role === 'user' ? 'user-message-content' : 'ai-message-content'}
                  />
                </div>
                
                {/* 消息底部信息 */}
                <div className="message-actions">
                  <span className={message.role === 'user' ? 'message-timestamp-user' : 'message-timestamp'}>
                    {message.timestamp instanceof Date ? message.timestamp.toLocaleTimeString('zh-CN', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    }) : message.timestamp}
                  </span>
                  <div className="message-action-buttons">
                    <button 
                      className="btn-action" 
                      title={copiedMessageId === message.id ? "已复制" : "复制"}
                      onClick={() => copyMessage(message.id)}
                      disabled={isProcessing}
                    >
                      {copiedMessageId === message.id ? (
                        <CheckIcon className="w-3.5 h-3.5 text-green-500 transition" />
                      ) : (
                        <ClipboardDocumentIcon className="w-3.5 h-3.5" />
                      )}
                    </button>
                    {message.role === 'user' && (
                      <button 
                        className="btn-action" 
                        title="编辑"
                        onClick={() => setEditingMessage({ id: message.id, content: message.content })}
                        disabled={isProcessing}
                      >
                        <PencilIcon className="w-3.5 h-3.5" />
                      </button>
                    )}
                    {message.role === 'assistant' && (
                      <>
                        <button 
                          className="btn-action" 
                          title="重新生成"
                          onClick={() => regenerateMessage(message.id)}
                          disabled={isProcessing || isLoading}
                        >
                          <ArrowPathIcon className="w-3.5 h-3.5" />
                        </button>
                      <button 
                        className={`btn-action ${message.metadata?.liked ? 'text-green-600 dark:text-green-400' : 'text-gray-400 dark:text-gray-500'}`}
                        title={message.metadata?.liked ? "取消喜欢" : "喜欢"}
                        aria-pressed={message.metadata?.liked}
                        aria-label={message.metadata?.liked ? "取消喜欢这条消息" : "喜欢这条消息"}
                        onClick={() => likeMessage(message.id)}
                        disabled={isProcessing}
                      >
                        <HandThumbUpIcon className="w-3.5 h-3.5" />
                      </button>
                      <button 
                        className={`btn-action ${message.metadata?.disliked ? 'text-red-600 dark:text-red-400' : 'text-gray-400 dark:text-gray-500'}`}
                        title={message.metadata?.disliked ? "取消不喜欢" : "不喜欢"}
                        aria-pressed={message.metadata?.disliked}
                        aria-label={message.metadata?.disliked ? "取消不喜欢这条消息" : "不喜欢这条消息"}
                        onClick={() => dislikeMessage(message.id)}
                        disabled={isProcessing}
                      >
                        <HandThumbDownIcon className="w-3.5 h-3.5" />
                      </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {/* 加载状态 */}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="message-bubble message-bubble-ai">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                  <span className="text-gray-500 dark:text-gray-400">AI 正在思考中...</span>
                </div>
              </div>
            </div>
          )}
          
          {/* 滚动目标元素 */}
          <div ref={messagesEndRef} className="h-1" />
        </div>
      </div>

      {/* 底部：输入区域 */}
      <div className="chat-input-container">
        <div className="chat-input-container-inner">
          <div className="chat-input-wrapper">
            {/* 三层输入结构 */}
            <div className="chat-input-area">
            {/* 上层：文件上传区域 */}
            <div className="chat-input-files">
              <div className="chat-input-files-content">
                <FileUpload
                  files={files}
                  onFilesChange={handleFilesChange}
                  maxFiles={5}
                  maxSize={10 * 1024 * 1024}
                  className="file-upload-chat"
                />
              </div>
            </div>

            {/* 中层：输入框 */}
            <div className="chat-input-main">
              <textarea
                ref={textareaRef}
                placeholder="输入消息..."
                className="chat-input-field"
                rows={1}
                style={{ minHeight: '24px', maxHeight: '120px', resize: 'none', overflow: 'hidden' }}
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                onCompositionStart={handleCompositionStart}
                onCompositionEnd={handleCompositionEnd}
                onPaste={handlePaste}
              />
            </div>

            {/* 下层：工具栏 */}
            <div className="chat-input-toolbar">
              <div className="chat-input-tools-left">
                <select className="model-selector">
                  <option>GPT-4</option>
                  <option>GPT-3.5</option>
                  <option>Claude</option>
                </select>
                <button className="tool-icon-btn" title="Token使用统计">
                  <InformationCircleIcon className="w-3.5 h-3.5" />
                </button>
                <button className="tool-icon-btn" title="设置">
                  <CogIcon className="w-3.5 h-3.5" />
                </button>
              </div>
              
              <div className="chat-input-tools-right">
                <button className="tool-icon-btn" title="语音输入">
                  <MicrophoneIcon className="w-3.5 h-3.5" />
                </button>
                <button className="tool-icon-btn" title="新对话">
                  <PlusIcon className="w-3.5 h-3.5" />
                </button>
                <button 
                  className={`send-btn ${isSending ? 'cancel-mode' : ''}`}
                  title={isSending ? "取消" : "发送"}
                  onClick={isSending ? handleCancel : handleSend}
                  disabled={!canSend && !isSending}
                >
                  {isSending ? (
                    <StopIcon className="w-3.5 h-3.5" />
                  ) : (
                    <PaperAirplaneIcon className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* 编辑消息模态框 */}
      <MessageEditModal
        isOpen={!!editingMessage}
        initialContent={editingMessage?.content || ''}
        onSave={handleEditSave}
        onCancel={handleEditCancel}
      />
    </div>
  );
};
