import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import { ThemeProvider } from "./context/ThemeContext.tsx";
import { useTheme } from "./hooks/useTheme";
import { SidebarProvider } from "./context/SidebarContext.tsx";
import { ConversationProvider } from "./context/ConversationContext.tsx";
import { ChatPage } from "./pages/ChatPage";
import { isAuthenticated } from "./utils/auth";

const AppContent: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [authenticated, setAuthenticated] = useState(isAuthenticated());

  console.log("AppContent render - authenticated:", authenticated);

  // 监听认证状态变化
  useEffect(() => {
    const checkAuth = () => {
      const authStatus = isAuthenticated();
      console.log("Auth status changed:", authStatus);
      setAuthenticated(authStatus);
    };

    // 监听新的authChanged事件（从新的auth.ts发出）
    window.addEventListener('authChanged', checkAuth);
    // 保持对旧的tokenChanged事件的兼容性
    window.addEventListener('tokenChanged', checkAuth);
    // 监听storage事件（当localStorage在其他标签页改变时触发）
    window.addEventListener('storage', checkAuth);

    return () => {
      window.removeEventListener('authChanged', checkAuth);
      window.removeEventListener('tokenChanged', checkAuth);
      window.removeEventListener('storage', checkAuth);
    };
  }, []);

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          authenticated ? (
            <ChatPage theme={theme} onToggleTheme={toggleTheme} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
    </Routes>
  );
};

function App() {
  return (
    <ThemeProvider>
      <SidebarProvider>
        <ConversationProvider>
          <BrowserRouter>
            <AppContent />
          </BrowserRouter>
        </ConversationProvider>
      </SidebarProvider>
    </ThemeProvider>
  );
}

export default App;
