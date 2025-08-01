export interface SidebarContextType {
  isCollapsed: boolean;
  isMobileOpen: boolean;
  toggleCollapse: () => void;
  toggleMobileOpen: () => void;
  setMobileOpen: (open: boolean) => void;
}
import { createContext } from 'react';
export const SidebarContext = createContext<SidebarContextType | undefined>(undefined);
