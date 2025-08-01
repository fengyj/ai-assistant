import { useContext } from 'react';
import { SidebarContext } from '../context/SidebarContext';
import type { SidebarContextType } from '../context/SidebarContext';

export const useSidebar = (): SidebarContextType => {
  const context = useContext(SidebarContext);
  if (context === undefined) {
    throw new Error('useSidebar must be used within a SidebarProvider');
  }
  return context;
};
