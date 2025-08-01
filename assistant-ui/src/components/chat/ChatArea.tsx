import React from 'react';
import { Button } from '../ui/Button';
import { useSidebar } from '../../hooks/useSidebar';
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

  // 输入框自动高度逻辑
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  const handleInput = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  };

  // 模拟消息数据
  const messages = [
    {
      id: '1',
      role: 'user' as const,
      content: '你好，我想了解一下React的useState Hook是如何工作的？',
      timestamp: '10:30',
    },
    {
      id: '2',
      role: 'assistant' as const,
      content: '你好！useState 是 React 中最基础也是最重要的 Hook 之一。\n\n它的主要作用是在函数组件中添加状态管理功能。基本语法如下：\n\n```javascript\nconst [state, setState] = useState(initialValue);\n```\n\n其中：\n- `state` 是当前的状态值\n- `setState` 是更新状态的函数\n- `initialValue` 是状态的初始值\n\n当你调用 `setState` 时，React 会重新渲染组件，并使用新的状态值。',
      timestamp: '10:31',
    },
  ];

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
                    {message.timestamp}
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
                onInput={handleInput}
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
                <button className="send-btn" title="发送">
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
