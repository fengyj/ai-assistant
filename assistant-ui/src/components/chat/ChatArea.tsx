import React from 'react';
import { Button } from '../ui/Button';
import { useSidebar } from '../../hooks/useSidebar';
import { useConversation } from '../../hooks/useConversation';
import { useChatInput } from '../../hooks/useChatInput';
import { 
  SunIcon, 
  MoonIcon, 
  PaperAirplaneIcon,
  MicrophoneIcon,
  PlusIcon,
  CogIcon,
  PaperClipIcon,
  ClipboardDocumentIcon,
  PencilIcon,
  ArrowPathIcon,
  HandThumbUpIcon,
  HandThumbDownIcon,
  InformationCircleIcon,
  Bars3Icon
} from '@heroicons/react/24/outline';

interface ChatAreaProps {
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({ theme, onToggleTheme }) => {
  const { toggleMobileOpen } = useSidebar();
  const { currentConversation, sendMessage, isLoading } = useConversation();
  
  // 使用聊天输入 Hook
  const {
    inputValue,
    textareaRef,
    canSend,
    handleSend,
    handleInputChange,
    handleKeyDown,
    handleCompositionStart,
    handleCompositionEnd,
  } = useChatInput({
    onSend: sendMessage,
  });

  // 获取当前对话的消息，如果没有对话则显示空数组
  const messages = currentConversation?.messages || [];

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
      <div className="message-container">
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
                  {message.content.split('\n').map((line, index) => {
                    if (line.startsWith('```javascript')) {
                      return (
                        <div key={index} className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4 my-3 border-l-4 border-blue-500">
                          <code className="text-sm font-mono text-blue-800 dark:text-blue-200">
                            {message.content.split('```javascript')[1]?.split('```')[0]}
                          </code>
                        </div>
                      );
                    }
                    if (line.startsWith('```')) {
                      return null; // 跳过代码块标记
                    }
                    if (line.trim() === '') {
                      return <br key={index} />;
                    }
                    return (
                      <p key={index} className={`mb-2 ${message.role === 'user' ? 'text-white' : 'text-gray-900 dark:text-gray-100'}`}>
                        {line}
                      </p>
                    );
                  })}
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
                    <button className="btn-action" title="复制">
                      <ClipboardDocumentIcon className="w-3.5 h-3.5" />
                    </button>
                    {message.role === 'user' && (
                      <button className="btn-action" title="编辑">
                        <PencilIcon className="w-3.5 h-3.5" />
                      </button>
                    )}
                    {message.role === 'assistant' && (
                      <>
                        <button className="btn-action" title="重新生成">
                          <ArrowPathIcon className="w-3.5 h-3.5" />
                        </button>
                        <button className="btn-action" title="喜欢">
                          <HandThumbUpIcon className="w-3.5 h-3.5" />
                        </button>
                        <button className="btn-action" title="不喜欢">
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
                <button className="file-upload-btn" title="上传文件">
                  <PaperClipIcon className="w-3.5 h-3.5" />
                </button>
                {/* 这里可以添加已上传文件的列表 */}
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
                  className="send-btn" 
                  title="发送"
                  onClick={handleSend}
                  disabled={!canSend}
                >
                  <PaperAirplaneIcon className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
