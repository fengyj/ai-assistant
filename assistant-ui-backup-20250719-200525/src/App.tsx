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
  // Custom hooks
  const { isDarkMode, toggleTheme } = useTheme();
  // 主题切换时自动设置 body class
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.body.classList.toggle('dark-theme', isDarkMode);
      document.body.classList.toggle('light-theme', !isDarkMode);
    }
  }, [isDarkMode]);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showLoginDialog, setShowLoginDialog] = useState(false);
  const [showSettingsDialog, setShowSettingsDialog] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
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

  // Toast 提示函数
  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

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
        content: generateAIResponse(currentMessage, currentFiles, getFileIcon),
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
    <div className="app-container">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="toast">
          <div className="toast-content">
            <div className="toast-message">
              <span className="toast-text">{toastMessage}</span>
            </div>
          </div>
        </div>
      )}
      
      {/* Login Dialog */}
      {showLoginDialog && (
        <div className="dialog-overlay">
          <div className="dialog">
            <h2 className="dialog-title">登录</h2>
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target as HTMLFormElement);
              handleLogin(
                formData.get('username') as string,
                formData.get('password') as string
              );
            }}>
              <div className="dialog-form">
                <div className="dialog-field">
                  <label className="dialog-label">用户名</label>
                  <input
                    type="text"
                    name="username"
                    required
                    className="dialog-input"
                    placeholder="请输入用户名"
                  />
                </div>
                <div className="dialog-field">
                  <label className="dialog-label">密码</label>
                  <input
                    type="password"
                    name="password"
                    required
                    className="dialog-input"
                    placeholder="请输入密码"
                  />
                </div>
              </div>
              <div className="dialog-actions">
                <button
                  type="button"
                  onClick={() => setShowLoginDialog(false)}
                  className="dialog-btn cancel"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="dialog-btn confirm"
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
        <div className="dialog-overlay">
          <div className="dialog">
            <h2 className="dialog-title">系统设置</h2>
            {/* User Info */}
            {user && (
              <div className="dialog-user-info">
                <div className="dialog-user-row">
                  <div className="avatar size-md">
                    {user.avatar ? (
                      <img src={user.avatar} alt={user.name} className="avatar-img" />
                    ) : (
                      <div className="avatar-fallback">
                        {user.name.charAt(0).toUpperCase()}
                      </div>
                    )}
                  </div>
                  <div>
                    <p className="dialog-user-name">{user.name}</p>
                    <p className="dialog-user-id">ID: {user.id}</p>
                  </div>
                </div>
              </div>
            )}
            {/* Settings Options */}
            <div className="dialog-options">
              <div className="dialog-option">
                <span className="dialog-option-label">深色模式</span>
                <button
                  onClick={toggleTheme}
                  className="theme-toggle"
                >
                  <div className="theme-toggle-dot"></div>
                </button>
              </div>
            </div>
            <div className="dialog-actions between">
              <button
                onClick={handleLogout}
                className="dialog-btn logout"
              >
                退出登录
              </button>
              <button
                onClick={() => setShowSettingsDialog(false)}
                className="dialog-btn cancel"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
      
      <div className="main-layout">
        {/* Sidebar */}
        <Sidebar
          isOpen={isSidebarOpen}
          conversations={conversations}
          currentConversationId={currentConversationId}
          user={user}
          onConversationSelect={setCurrentConversationId}
          onConversationDelete={deleteConversation}
          onUserStatusClick={handleUserStatusClick}
        />
        
        {/* Main Content */}
        <div className="main-content">
          {/* Header */}
          <div className="header">
            <div className="header-content">
              <div className="header-left">
                <button
                  onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                  className="header-toggle"
                >
                  <span className="header-toggle-icon">
                    {isSidebarOpen ? '◀' : '▶'}
                  </span>
                </button>
                <h1 className="header-title">
                  {currentConversation?.title || 'AI Assistant'}
                </h1>
              </div>
              <button
                onClick={toggleTheme}
                className="header-theme-btn"
              >
                {isDarkMode ? '🌙' : '☀️'}
              </button>
            </div>
          </div>
          
          {/* Messages */}
          <div className="messages-container" ref={messagesContainerRef}>
            {currentConversation && (
              <div className="messages-wrapper">
                {currentConversation.messages.map((msg) => (
                  <MessageComponent key={msg.id} message={msg} />
                ))}
                
                {isLoading && <LoadingIndicator />}
              </div>
            )}
          </div>
          
          {/* Chat Input */}
          <ChatInput
            message={message}
            selectedFiles={selectedFiles}
            isLoading={isLoading}
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
