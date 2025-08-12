import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import { ThemeProvider } from "./context/ThemeContext.tsx";
import { useTheme } from "./hooks/useTheme";
import { SidebarProvider } from "./context/SidebarContext.tsx";
import { ConversationProvider } from "./context/ConversationContext.tsx";
import { UserSessionProvider } from "./context/UserSessionContext.tsx";
import { useUserSession } from "./hooks/useUserSession";
import { ChatPage } from "./pages/ChatPage";
import { AppInitializing } from "./components/ui/AppInitializing";

const AppContent: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const { isAuthenticated, isInitializing, user } = useUserSession();

  console.log("AppContent render - isAuthenticated:", isAuthenticated, "isInitializing:", isInitializing, "user:", user?.username);

  // 如果正在初始化，显示加载状态
  if (isInitializing) {
    return <AppInitializing message="正在恢复用户会话..." />;
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          isAuthenticated ? (
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
    <UserSessionProvider>
      <ThemeProvider>
        <SidebarProvider>
          <ConversationProvider>
            <BrowserRouter>
              <AppContent />
            </BrowserRouter>
          </ConversationProvider>
        </SidebarProvider>
      </ThemeProvider>
    </UserSessionProvider>
  );
}

export default App;
