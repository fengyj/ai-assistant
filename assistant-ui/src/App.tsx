import React from 'react';
import { ThemeProvider } from './context/ThemeContext.tsx';
import { useTheme } from './hooks/useTheme';
import { SidebarProvider } from './context/SidebarContext.tsx';
import { ChatPage } from './pages/ChatPage';

const AppContent: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="app-container">
      <ChatPage theme={theme} onToggleTheme={toggleTheme} />
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <SidebarProvider>
        <AppContent />
      </SidebarProvider>
    </ThemeProvider>
  );
}

export default App;
