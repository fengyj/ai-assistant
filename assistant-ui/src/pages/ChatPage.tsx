import React from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import Sidebar from '../components/sidebar/Sidebar';
import { ChatArea } from '../components/chat/ChatArea';

interface ChatPageProps {
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export const ChatPage: React.FC<ChatPageProps> = ({ theme, onToggleTheme }) => {
  return (
    <MainLayout
      sidebar={<Sidebar />}
      main={<ChatArea theme={theme} onToggleTheme={onToggleTheme} />}
    />
  );
};
