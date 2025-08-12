import { createContext } from 'react';
import type { UserInfo } from '../utils/auth';

export interface UserSessionContextType {
  user: UserInfo | null;
  setUser: (user: UserInfo | null) => void;
  logout: () => void;
  isAuthenticated: boolean;
  isInitializing: boolean;
  accessToken: string | null;
  tokenType: string | null;
  sessionId: string | null;
  expiryTime: number | null;
  refreshToken: () => Promise<string | null>;
  isTokenExpiringSoon: () => boolean;
}

export const UserSessionContext = createContext<UserSessionContextType | undefined>(undefined);
