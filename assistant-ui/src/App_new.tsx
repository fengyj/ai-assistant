import { useState, useEffect, useRef } from 'react';
import { useConversations } from './hooks/useConversations';
import { useFileUpload } from './hooks/useFileUpload';
import { useTheme } from './hooks/useTheme';
import { useAuth } from './hooks/useAuth';
import { generateAIResponse } from './utils/conversationUtils';
import { Sidebar } from './components/Sidebar';
import { MessageComponent } from './components/MessageComponent';
import { LoadingIndicator } from './components/LoadingIndicator';
import { ChatInput } from './components/ChatInput';
import type { Message } from './types';

export default function App() {
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showLoginDialog, setShowLoginDialog] = useState(false);
  const [showSettingsDialog, setShowSettingsDialog] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Custom hooks
  const { isDarkMode, toggleTheme } = useTheme();
  const { user, login, logout } = useAuth();
  const {
    conversations,
    currentConversation,
    currentConversationId,
    setCurrentConversationId,
    createNewConversation,
    deleteConversation,
    addMessage,
    updateConversationTitle
  } = useConversations();
  
  const {
    selectedFiles,
    isDragOver,
    getFileIcon,
    handleFileSelect,
    removeFile,
    clearFiles,
    handleDragOver,
    handleDragLeave,
    handleDrop
  } = useFileUpload();

  // Auto scroll to latest message
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [currentConversation?.messages, isLoading]);

  // Toast notification
  const showToast = (message: string) => {
    setToastMessage(message);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // Handle paste events for file upload
  useEffect(() => {
    const handleGlobalPaste = (e: ClipboardEvent) => {
      const activeElement = document.activeElement;
      const isInputFocused = activeElement?.tagName === 'TEXTAREA';
      
      if (isInputFocused && e.clipboardData?.items) {
        const files: File[] = [];
        
        for (let i = 0; i < e.clipboardData.items.length; i++) {
          const item = e.clipboardData.items[i];
          
          if (item.kind === 'file') {
            const file = item.getAsFile();
            if (file) {
              if (file.type.startsWith('image/')) {
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const fileExtension = file.type.split('/')[1] || 'png';
                const renamedFile = new File([file], `screenshot-${timestamp}.${fileExtension}`, {
                  type: file.type
                });
                files.push(renamedFile);
              } else {
                files.push(file);
              }
            }
          }
        }
        
        if (files.length > 0) {
          e.preventDefault();
          handleFileSelect(files);
          showToast(`✅ 已粘贴 ${files.length} 个文件`);
        }
      }
    };
    
    document.addEventListener('paste', handleGlobalPaste);
    return () => document.removeEventListener('paste', handleGlobalPaste);
  }, [handleFileSelect]);

  // Send message
  const sendMessage = () => {
    if ((!message.trim() && selectedFiles.length === 0) || !currentConversationId) return;
    
    // Build message content
    let messageContent = message;
    if (selectedFiles.length > 0) {
      const fileList = selectedFiles.map(file => 
        `📎 ${file.name} (${(file.size / 1024).toFixed(1)}KB)`
      ).join('\n');
      messageContent = message ? `${message}\n\n**附件：**\n${fileList}` : `**附件：**\n${fileList}`;
    }
    
    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageContent,
      isUser: true,
      timestamp: new Date()
    };
    
    addMessage(currentConversationId, userMessage);
    
    // Update conversation title if first user message
    if (currentConversation?.messages.filter(m => m.isUser).length === 0) {
      const titleText = message || (selectedFiles.length > 0 ? `${selectedFiles.length}个文件` : 'New Chat');
      updateConversationTitle(currentConversationId, titleText);
    }
    
    const currentMessage = message;
    const currentFiles = [...selectedFiles];
    setMessage('');
    clearFiles();
    setIsLoading(true);
    
    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: generateAIResponse(currentMessage, currentFiles),
        isUser: false,
        timestamp: new Date()
      };
      
      addMessage(currentConversationId, aiMessage);
      setIsLoading(false);
    }, 1000);
  };

  const cancelRequest = () => {
    setIsLoading(false);
    showToast('已取消生成');
  };

  const handleUserStatusClick = () => {
    if (user) {
      setShowSettingsDialog(true);
    } else {
      setShowLoginDialog(true);
    }
  };

  const handleLogin = (username: string, password: string) => {
    if (login(username, password)) {
      setShowLoginDialog(false);
      showToast('登录成功');
    }
  };

  const handleLogout = () => {
    logout();
    setShowSettingsDialog(false);
    showToast('已退出登录');
  };

  return (
    <div className={`min-h-screen ${isDarkMode ? 'dark bg-gray-900' : 'bg-gray-50'} transition-colors`}>
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-4 right-4 z-50 animate-fade-in">
          <div className={`px-4 py-3 rounded-lg shadow-lg ${
            isDarkMode 
              ? 'bg-gray-800 text-white border border-gray-700' 
              : 'bg-white text-gray-800 border border-gray-200'
          }`}>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium">{toastMessage}</span>
            </div>
          </div>
        </div>
      )}
      
      {/* Login Dialog */}
      {showLoginDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-white'} rounded-lg p-6 w-96 max-w-sm mx-4`}>
            <h2 className={`text-xl font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              登录
            </h2>
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target as HTMLFormElement);
              handleLogin(
                formData.get('username') as string,
                formData.get('password') as string
              );
            }}>
              <div className="space-y-4">
                <div>
                  <label className={`block text-sm font-medium mb-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    用户名
                  </label>
                  <input
                    type="text"
                    name="username"
                    required
                    className={`w-full px-3 py-2 border rounded-md ${
                      isDarkMode 
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                    } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                    placeholder="请输入用户名"
                  />
                </div>
                <div>
                  <label className={`block text-sm font-medium mb-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    密码
                  </label>
                  <input
                    type="password"
                    name="password"
                    required
                    className={`w-full px-3 py-2 border rounded-md ${
                      isDarkMode 
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                    } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                    placeholder="请输入密码"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowLoginDialog(false)}
                  className={`px-4 py-2 rounded-md ${
                    isDarkMode 
                      ? 'text-gray-300 hover:bg-gray-700' 
                      : 'text-gray-700 hover:bg-gray-100'
                  } transition-colors`}
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  登录
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Settings Dialog */}
      {showSettingsDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-white'} rounded-lg p-6 w-96 max-w-sm mx-4`}>
            <h2 className={`text-xl font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              系统设置
            </h2>
            
            {/* User Info */}
            {user && (
              <div className="mb-6">
                <div className="flex items-center space-x-3 mb-4 shrink-0">
                  <div className="w-12 h-12 rounded-full overflow-hidden bg-gray-300">
                    {user.avatar ? (
                      <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
                    ) : (
                      <div className={`w-full h-full flex items-center justify-center text-lg font-medium ${
                        isDarkMode ? 'bg-gray-600 text-white' : 'bg-gray-300 text-gray-700'
                      }`}>
                        {user.name.charAt(0).toUpperCase()}
                      </div>
                    )}
                  </div>
                  <div>
                    <p className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                      {user.name}
                    </p>
                    <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                      ID: {user.id}
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            {/* Settings Options */}
            <div className="space-y-3 mb-6">
              <div className={`flex items-center justify-between p-3 rounded-md ${
                isDarkMode ? 'bg-gray-700' : 'bg-gray-50'
              }`}>
                <span className={`text-sm ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                  深色模式
                </span>
                <button
                  onClick={toggleTheme}
                  className={`w-12 h-6 rounded-full p-1 ${
                    isDarkMode ? 'bg-blue-600' : 'bg-gray-300'
                  } transition-colors`}
                >
                  <div className={`w-4 h-4 rounded-full bg-white transform transition-transform ${
                    isDarkMode ? 'translate-x-6' : 'translate-x-0'
                  }`}></div>
                </button>
              </div>
            </div>
            
            <div className="flex justify-between">
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
              >
                退出登录
              </button>
              <button
                onClick={() => setShowSettingsDialog(false)}
                className={`px-4 py-2 rounded-md ${
                  isDarkMode 
                    ? 'text-gray-300 hover:bg-gray-700' 
                    : 'text-gray-700 hover:bg-gray-100'
                } transition-colors`}
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
      
      <div className="flex h-screen">
        {/* Sidebar */}
        <Sidebar
          isOpen={isSidebarOpen}
          conversations={conversations}
          currentConversationId={currentConversationId}
          user={user}
          isDarkMode={isDarkMode}
          onConversationSelect={setCurrentConversationId}
          onConversationDelete={deleteConversation}
          onUserStatusClick={handleUserStatusClick}
        />
        
        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
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
              
              <button
                onClick={toggleTheme}
                className={`p-2 rounded-lg ${isDarkMode ? 'bg-gray-700 text-yellow-400' : 'bg-gray-100 text-gray-600'} hover:opacity-80`}
              >
                {isDarkMode ? '🌙' : '☀️'}
              </button>
            </div>
          </div>
          
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4" ref={messagesContainerRef}>
            {currentConversation && (
              <div className="max-w-4xl mx-auto space-y-4">
                {currentConversation.messages.map((msg) => (
                  <MessageComponent key={msg.id} message={msg} />
                ))}
                
                {isLoading && <LoadingIndicator isDarkMode={isDarkMode} />}
              </div>
            )}
          </div>
          
          {/* Chat Input */}
          <ChatInput
            message={message}
            selectedFiles={selectedFiles}
            isLoading={isLoading}
            isDarkMode={isDarkMode}
            isDragOver={isDragOver}
            onMessageChange={setMessage}
            onFileSelect={handleFileSelect}
            onRemoveFile={removeFile}
            onSendMessage={sendMessage}
            onCancelRequest={cancelRequest}
            onCreateNewConversation={createNewConversation}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            getFileIcon={getFileIcon}
          />
        </div>
      </div>
    </div>
  );
}
