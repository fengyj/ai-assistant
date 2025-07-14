import { useState, useEffect } from 'react';

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

export default function App() {
  // 主题状态
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  // 侧边栏状态
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  // 对话状态
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  
  // 消息输入状态
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // 模型选择
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  
  // 获取当前对话
  const currentConversation = conversations.find(c => c.id === currentConversationId);
  
  // 简单的Markdown渲染函数
  const renderMarkdown = (text: string) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      .replace(/`([^`]+)`/g, '<code class="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm font-mono">$1</code>')
      .replace(/\n/g, '<br />');
  };
  
  // 初始化默认对话
  useEffect(() => {
    if (conversations.length === 0) {
      const defaultConversation: Conversation = {
        id: '1',
        title: 'New Chat',
        messages: [{
          id: '1',
          content: 'Hello! I\'m your AI assistant. How can I help you today?',
          isUser: false,
          timestamp: new Date()
        }],
        createdAt: new Date()
      };
      setConversations([defaultConversation]);
      setCurrentConversationId('1');
    }
  }, [conversations.length]);
  
  // 主题切换
  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };
  
  // 创建新对话
  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [{
        id: Date.now().toString(),
        content: 'Hello! I\'m your AI assistant. How can I help you today?',
        isUser: false,
        timestamp: new Date()
      }],
      createdAt: new Date()
    };
    setConversations(prev => [newConversation, ...prev]);
    setCurrentConversationId(newConversation.id);
  };
  
  // 删除对话
  const deleteConversation = (id: string) => {
    setConversations(prev => prev.filter(c => c.id !== id));
    if (currentConversationId === id) {
      const remaining = conversations.filter(c => c.id !== id);
      setCurrentConversationId(remaining.length > 0 ? remaining[0].id : null);
    }
  };
  
  // 发送消息
  const sendMessage = () => {
    if (!message.trim() || !currentConversationId) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      content: message,
      isUser: true,
      timestamp: new Date()
    };
    
    // 更新对话消息
    setConversations(prev => prev.map(conv => 
      conv.id === currentConversationId 
        ? { ...conv, messages: [...conv.messages, userMessage] }
        : conv
    ));
    
    // 更新对话标题（如果是第一条用户消息）
    if (currentConversation?.messages.filter(m => m.isUser).length === 0) {
      setConversations(prev => prev.map(conv => 
        conv.id === currentConversationId 
          ? { ...conv, title: message.length > 30 ? message.substring(0, 30) + '...' : message }
          : conv
      ));
    }
    
    const currentMessage = message;
    setMessage('');
    setIsLoading(true);
    
    // 模拟AI回复
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: generateAIResponse(currentMessage),
        isUser: false,
        timestamp: new Date()
      };
      
      setConversations(prev => prev.map(conv => 
        conv.id === currentConversationId 
          ? { ...conv, messages: [...conv.messages, aiMessage] }
          : conv
      ));
      setIsLoading(false);
    }, 1000);
  };
  
  // 生成AI回复（模拟）
  const generateAIResponse = (userMessage: string) => {
    const responses = [
      `I understand you said: "${userMessage}". Here's my response with **markdown** support!`,
      `Thank you for your message about "${userMessage}". I can help you with:
      
## Features
- **Markdown rendering**
- *Italic text*
- \`inline code\`
- [Links](https://example.com)

### Code Example
\`\`\`javascript
console.log("Hello, World!");
\`\`\`

How can I assist you further?`,
      `Regarding "${userMessage}", I'd be happy to help! Here are some key points:

1. **Understanding**: I can process various types of questions
2. **Formatting**: I support rich text formatting
3. **Code**: I can handle code snippets and explanations

What would you like to explore next?`
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  };
  
  return (
    <div className={`min-h-screen ${isDarkMode ? 'dark bg-gray-900' : 'bg-gray-50'} transition-colors`}>
      <div className="flex h-screen">
        {/* 侧边栏 */}
        <div className={`${isSidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 overflow-hidden ${isDarkMode ? 'bg-gray-800' : 'bg-white'} border-r ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className={`text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                AI Assistant
              </h2>
              <button
                onClick={toggleTheme}
                className={`p-2 rounded-lg ${isDarkMode ? 'bg-gray-700 text-yellow-400' : 'bg-gray-100 text-gray-600'} hover:opacity-80`}
              >
                {isDarkMode ? '🌙' : '☀️'}
              </button>
            </div>
            
            <button
              onClick={createNewConversation}
              className={`w-full p-3 rounded-lg ${isDarkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white font-medium transition-colors`}
            >
              + New Chat
            </button>
            
            <div className="mt-4">
              <h3 className={`text-sm font-medium ${isDarkMode ? 'text-gray-400' : 'text-gray-600'} mb-2`}>
                Recent Conversations
              </h3>
              <div className="space-y-2">
                {conversations.map(conv => (
                  <div
                    key={conv.id}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      currentConversationId === conv.id
                        ? (isDarkMode ? 'bg-blue-900/50 border-blue-500' : 'bg-blue-50 border-blue-200')
                        : (isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50')
                    } border`}
                    onClick={() => setCurrentConversationId(conv.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-800'} truncate`}>
                          {conv.title}
                        </p>
                        <p className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                          {conv.createdAt.toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteConversation(conv.id);
                        }}
                        className={`p-1 rounded ${isDarkMode ? 'hover:bg-gray-600 text-gray-400' : 'hover:bg-gray-200 text-gray-500'}`}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        
        {/* 主要内容区域 */}
        <div className="flex-1 flex flex-col">
          {/* 顶部工具栏 */}
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-b p-4`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                  className={`p-2 rounded-lg ${isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
                >
                  <span className={`text-xl ${isDarkMode ? 'text-white' : 'text-gray-700'}`}>
                    {isSidebarOpen ? '◀' : '▶'}
                  </span>
                </button>
                <h1 className={`text-xl font-semibold ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                  {currentConversation?.title || 'AI Assistant'}
                </h1>
              </div>
              
              <div className="flex items-center space-x-4">
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className={`px-3 py-2 rounded-lg border ${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-700'} focus:ring-2 focus:ring-blue-500`}
                >
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-3.5">GPT-3.5 Turbo</option>
                  <option value="claude">Claude</option>
                </select>
              </div>
            </div>
          </div>
          
          {/* 消息显示区域 */}
          <div className="flex-1 overflow-y-auto p-4">
            {currentConversation && (
              <div className="max-w-4xl mx-auto space-y-4">
                {currentConversation.messages.map((msg) => (
                  <div key={msg.id} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xl px-4 py-3 rounded-lg ${
                      msg.isUser 
                        ? 'bg-blue-500 text-white' 
                        : (isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-800 border border-gray-200')
                    } shadow-sm`}>
                      {msg.isUser ? (
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      ) : (
                        <div 
                          className={`${isDarkMode ? 'text-white' : 'text-gray-800'}`}
                          dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
                        />
                      )}
                      <p className={`text-xs mt-2 ${
                        msg.isUser ? 'text-blue-100' : (isDarkMode ? 'text-gray-400' : 'text-gray-500')
                      }`}>
                        {msg.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className={`max-w-xl px-4 py-3 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white border border-gray-200'} shadow-sm`}>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        <span className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>AI is thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* 消息输入区域 */}
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-t p-4`}>
            <div className="max-w-4xl mx-auto">
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Type your message..."
                  className={`flex-1 px-4 py-3 rounded-lg border ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-700 placeholder-gray-500'
                  } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={!message.trim() || isLoading}
                  className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  {isLoading ? 'Sending...' : 'Send'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
