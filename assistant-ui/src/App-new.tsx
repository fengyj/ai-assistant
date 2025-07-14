import { useState, useEffect, useRef } from 'react';

// 类型定义
interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

interface AIModel {
  id: string;
  name: string;
  description: string;
  isAvailable: boolean;
}

interface AppState {
  user: User;
  conversations: Conversation[];
  currentConversation: Conversation | null;
  selectedModel: AIModel | null;
  availableModels: AIModel[];
  theme: 'light' | 'dark';
  isLoading: boolean;
}

// 模拟数据
const mockModels: AIModel[] = [
  { id: 'gpt-4', name: 'GPT-4', description: 'Most capable model', isAvailable: true },
  { id: 'gpt-3.5', name: 'GPT-3.5 Turbo', description: 'Fast and efficient', isAvailable: true },
  { id: 'claude-3', name: 'Claude 3', description: 'Anthropic\'s model', isAvailable: true },
];

const mockUser: User = {
  id: '1',
  name: 'John Doe',
  email: 'john@example.com',
  avatar: '/default-avatar.svg'
};

const mockConversations: Conversation[] = [
  {
    id: '1',
    title: 'Welcome Conversation',
    createdAt: new Date(),
    messages: [
      {
        id: '1',
        content: 'Hello! How can I help you today?',
        isUser: false,
        timestamp: new Date(),
      }
    ]
  }
];

export default function App() {
  const [appState, setAppState] = useState<AppState>({
    user: mockUser,
    conversations: mockConversations,
    currentConversation: mockConversations[0],
    selectedModel: mockModels[0],
    availableModels: mockModels,
    theme: 'light',
    isLoading: false,
  });

  const [inputMessage, setInputMessage] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [appState.currentConversation?.messages]);

  // 自动调整文本区域高度
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputMessage]);

  // 切换主题
  const toggleTheme = () => {
    setAppState(prev => ({
      ...prev,
      theme: prev.theme === 'light' ? 'dark' : 'light'
    }));
  };

  // 生成Markdown格式的回复
  const generateMarkdownResponse = (userMessage: string): string => {
    const responses = [
      `# 关于 "${userMessage}" 的回应

这是一个 **Markdown 格式** 的回应，包含多种元素：

## 代码示例
\`\`\`javascript
function greet(name) {
  console.log(\`Hello, \${name}!\`);
}
greet("World");
\`\`\`

## 列表
- 项目 1
- 项目 2
  - 子项目 2.1
  - 子项目 2.2

## 表格
| 特性 | 状态 | 描述 |
|------|------|------|
| Markdown 渲染 | ✅ | 支持完整的 Markdown 语法 |
| 代码高亮 | ✅ | 支持语法高亮 |
| 响应式设计 | ✅ | 适配各种屏幕尺寸 |

## 引用
> 这是一个引用块，展示了 Markdown 的引用功能。

## 链接
访问 [GitHub](https://github.com) 了解更多信息。

*这是斜体文本*，**这是粗体文本**。

\`inline code\` 也被支持。`,

      `## 技术分析

您提到的 "${userMessage}" 是一个很好的话题。让我从几个方面来分析：

### 1. 核心概念
- **定义**: 这是一个重要的技术概念
- **应用**: 广泛应用于现代软件开发中

### 2. 代码实现
\`\`\`python
# Python 示例
def process_data(data):
    """处理数据的函数"""
    result = []
    for item in data:
        if item.is_valid():
            result.append(item.transform())
    return result

# 使用示例
data = load_data()
processed = process_data(data)
print(f"处理了 {len(processed)} 个项目")
\`\`\`

### 3. 最佳实践
1. **性能优化**: 使用合适的数据结构
2. **错误处理**: 添加适当的异常处理
3. **测试**: 编写单元测试和集成测试

### 4. 参考资源
- [官方文档](https://example.com)
- [最佳实践指南](https://example.com/best-practices)

> 💡 **提示**: 在实际项目中，建议先进行小规模测试，然后逐步扩展。`,

      `# 快速回复

感谢您的问题："${userMessage}"

## 简要说明
这是一个 **演示性回复**，展示了我们的 Markdown 渲染功能：

- ✅ 支持 **粗体** 和 *斜体*
- ✅ 支持 \`内联代码\`
- ✅ 支持代码块：

\`\`\`bash
# 示例命令
npm install
npm run dev
\`\`\`

---

**注意**: 这是一个模拟回复，在实际应用中会连接到真实的 AI 模型。

如需更多信息，请参考 [文档](https://example.com)。`
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  };

  // 发送消息
  const sendMessage = async () => {
    if (!inputMessage.trim() || !appState.currentConversation) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      isUser: true,
      timestamp: new Date(),
    };

    // 添加用户消息
    setAppState(prev => ({
      ...prev,
      currentConversation: prev.currentConversation ? {
        ...prev.currentConversation,
        messages: [...prev.currentConversation.messages, newMessage],
      } : null,
      isLoading: true,
    }));

    setInputMessage('');

    // 模拟AI回复
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: generateMarkdownResponse(inputMessage),
        isUser: false,
        timestamp: new Date(),
      };

      setAppState(prev => ({
        ...prev,
        currentConversation: prev.currentConversation ? {
          ...prev.currentConversation,
          messages: [...prev.currentConversation.messages, aiMessage],
        } : null,
        isLoading: false,
      }));
    }, 1500);
  };

  // 创建新对话
  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'New Conversation',
      messages: [],
      createdAt: new Date(),
    };

    setAppState(prev => ({
      ...prev,
      conversations: [newConversation, ...prev.conversations],
      currentConversation: newConversation,
    }));
  };

  // 选择对话
  const selectConversation = (conversation: Conversation) => {
    setAppState(prev => ({
      ...prev,
      currentConversation: conversation,
    }));
    setIsSidebarOpen(false);
  };

  // 复制消息
  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  // 删除消息
  const deleteMessage = (messageId: string) => {
    setAppState(prev => ({
      ...prev,
      currentConversation: prev.currentConversation ? {
        ...prev.currentConversation,
        messages: prev.currentConversation.messages.filter(m => m.id !== messageId),
      } : null,
    }));
  };

  // 重新生成回复
  const regenerateResponse = (messageId: string) => {
    // 在实际实现中，这里会重新调用AI API
    console.log('重新生成回复:', messageId);
  };

  // 编辑消息
  const editMessage = (messageId: string) => {
    // 在实际实现中，这里会允许编辑消息
    console.log('编辑消息:', messageId);
  };

  // 处理键盘事件
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className={`flex h-screen bg-gray-50 ${appState.theme === 'dark' ? 'dark' : ''}`}>
      {/* 侧边栏 */}
      <div className={`flex flex-col bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ${
        isSidebarOpen ? 'w-80' : 'w-0 md:w-16'
      } md:relative absolute inset-y-0 left-0 z-40 ${isSidebarOpen ? 'shadow-lg md:shadow-none' : ''}`}>
        
        {/* 移动端遮罩 */}
        {isSidebarOpen && (
          <div 
            className="fixed inset-0 bg-black/50 md:hidden z-30" 
            onClick={() => setIsSidebarOpen(false)}
          />
        )}
        
        <div className="flex flex-col h-full relative z-40 bg-white dark:bg-gray-900">
          {/* 侧边栏头部 */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                {isSidebarOpen ? (
                  <span className="w-6 h-6 text-xl md:hidden">✕</span>
                ) : (
                  <span className="w-6 h-6 text-xl">☰</span>
                )}
                <span className="w-6 h-6 text-xl hidden md:block">💬</span>
              </button>
              {isSidebarOpen && (
                <button
                  onClick={createNewConversation}
                  className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <span className="w-6 h-6 text-xl">+</span>
                </button>
              )}
            </div>
          </div>

          {/* 对话列表 */}
          {isSidebarOpen && (
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {appState.conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => selectConversation(conversation)}
                  className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                    appState.currentConversation?.id === conversation.id
                      ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
                      : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                  }`}
                >
                  <span className="w-5 h-5 text-base">💬</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{conversation.title}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                      {conversation.messages.length} messages
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* 用户信息区域 */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            {isSidebarOpen ? (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {appState.user ? (
                    <button
                      onClick={() => setIsSettingsModalOpen(true)}
                      className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                      <img
                        src={appState.user.avatar || '/default-avatar.svg'}
                        alt={appState.user.name}
                        className="w-8 h-8 rounded-full object-cover"
                        onError={(e) => {
                          e.currentTarget.src = '/default-avatar.svg';
                        }}
                      />
                      <div className="text-left">
                        <p className="text-sm font-medium">{appState.user.name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Online</p>
                      </div>
                    </button>
                  ) : (
                    <button 
                      onClick={() => setIsLoginModalOpen(true)}
                      className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
                    >
                      <span className="w-6 h-6 text-xl">👤</span>
                      Login
                    </button>
                  )}
                </div>
                <button
                  onClick={toggleTheme}
                  className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  {appState.theme === 'light' ? (
                    <span className="w-5 h-5 text-base">🌙</span>
                  ) : (
                    <span className="w-5 h-5 text-base">☀️</span>
                  )}
                </button>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                <button
                  onClick={toggleTheme}
                  className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  {appState.theme === 'light' ? (
                    <span className="w-5 h-5 text-base">🌙</span>
                  ) : (
                    <span className="w-5 h-5 text-base">☀️</span>
                  )}
                </button>
                <button 
                  onClick={() => setIsLoginModalOpen(true)}
                  className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <span className="w-5 h-5 text-base">👤</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="flex-1 flex flex-col">
        {/* 顶部栏 */}
        <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setIsSidebarOpen(true)}
                className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <span className="w-6 h-6 text-xl">☰</span>
              </button>
              <div>
                <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {appState.currentConversation?.title || 'Select a conversation'}
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {appState.selectedModel?.name || 'No Model'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 消息区域 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {appState.currentConversation?.messages.map((message) => (
            <div key={message.id} className="group">
              {/* 消息头部 */}
              <div className={`flex items-start gap-3 ${message.isUser ? 'flex-row-reverse' : ''}`}>
                {/* 头像 */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.isUser 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 dark:bg-gray-700'
                }`}>
                  {message.isUser ? (
                    <span className="w-5 h-5 text-white text-base">👤</span>
                  ) : (
                    <span className="w-5 h-5 text-base">🤖</span>
                  )}
                </div>

                {/* 消息内容 */}
                <div className={`flex flex-col max-w-[80%] md:max-w-[70%] ${
                  message.isUser ? 'items-end' : 'items-start'
                }`}>
                  <div className={`rounded-2xl px-4 py-2 shadow-sm ${
                    message.isUser 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
                  }`}>
                    <div className={`prose max-w-none ${message.isUser ? 'prose-invert' : 'dark:prose-invert'}`}>
                      {/* 简单的Markdown渲染 */}
                      <div 
                        className="text-sm whitespace-pre-wrap"
                        dangerouslySetInnerHTML={{
                          __html: message.content
                            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                            .replace(/\*(.*?)\*/g, '<em>$1</em>')
                            .replace(/`(.*?)`/g, '<code class="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-xs">$1</code>')
                            .replace(/\n/g, '<br>')
                        }}
                      />
                    </div>
                  </div>
                  
                  {/* 消息操作 */}
                  <div className="flex items-center gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                    <div className="flex gap-1 ml-2">
                      {message.isUser ? (
                        <>
                          <button
                            onClick={() => editMessage(message.id)}
                            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                            title="Edit"
                          >
                            <span className="w-3 h-3 text-xs">✏️</span>
                          </button>
                          <button
                            onClick={() => deleteMessage(message.id)}
                            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                            title="Delete"
                          >
                            <span className="w-3 h-3 text-xs">🗑️</span>
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={() => copyMessage(message.content)}
                            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                            title="Copy"
                          >
                            <span className="w-3 h-3 text-xs">📋</span>
                          </button>
                          <button
                            onClick={() => regenerateResponse(message.id)}
                            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                            title="Regenerate"
                          >
                            <span className="w-3 h-3 text-xs">🔄</span>
                          </button>
                          <button
                            onClick={() => deleteMessage(message.id)}
                            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                            title="Delete"
                          >
                            <span className="w-3 h-3 text-xs">🗑️</span>
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {appState.isLoading && (
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                <span className="w-5 h-5 text-base">🤖</span>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-2xl px-4 py-2 shadow-sm border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end gap-2">
              {/* 附件按钮 */}
              <button className="p-3 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors">
                <span className="w-5 h-5 text-gray-600 dark:text-gray-400">📷</span>
              </button>

              {/* 输入框 */}
              <div className="flex-1 relative">
                <textarea
                  ref={textareaRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  className="w-full p-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={1}
                  style={{ minHeight: '48px', maxHeight: '120px' }}
                />
                
                {/* 模型选择 */}
                <div className="absolute right-2 top-2">
                  <select 
                    value={appState.selectedModel?.id || ''}
                    onChange={(e) => {
                      const model = appState.availableModels.find(m => m.id === e.target.value);
                      setAppState(prev => ({ ...prev, selectedModel: model || null }));
                    }}
                    className="text-xs border-none bg-transparent text-gray-500 dark:text-gray-400 focus:ring-0"
                  >
                    {appState.availableModels.map((model) => (
                      <option key={model.id} value={model.id}>
                        {model.name}
                      </option>
                    ))}
                  </select>
                  <span className="w-4 h-4 text-gray-500 dark:text-gray-400">⌄</span>
                </div>
              </div>

              {/* 发送按钮 */}
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || appState.isLoading}
                className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span className="w-5 h-5 text-base">📤</span>
              </button>
            </div>

            {/* 底部操作 */}
            <div className="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
              <div className="flex items-center gap-4">
                <span>Press Enter to send, Shift+Enter for new line</span>
              </div>
              <button className="flex items-center gap-1 hover:text-gray-700 dark:hover:text-gray-300">
                <span className="w-5 h-5 text-gray-600 dark:text-gray-400">⚙️</span>
                Settings
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
