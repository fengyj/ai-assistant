import { useContext } from 'react';
import { UserSessionContext } from '../context/UserSessionContext';

export const useUserSession = () => {
  const context = useContext(UserSessionContext);
  if (context === undefined) {
    throw new Error('useUserSession must be used within a UserSessionProvider');
  }
  return context;
};
