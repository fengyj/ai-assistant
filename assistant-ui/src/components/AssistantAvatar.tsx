import { type FC } from 'react';
import type { User } from '../types';

interface AssistantAvatarProps {
  user?: User | null;
  size?: 'sm' | 'md' | 'lg';
  isDarkMode?: boolean;
}

export const AssistantAvatar: FC<AssistantAvatarProps> = ({ 
  user, 
  size = 'md',
  isDarkMode = false 
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8 text-sm',
    md: 'w-12 h-12 text-lg',
    lg: 'w-16 h-16 text-xl'
  };

  if (!user) {
    return (
      <div className={`${sizeClasses[size]} rounded-full flex items-center justify-center ${
        isDarkMode ? 'bg-gray-600 text-gray-300' : 'bg-gray-200 text-gray-600'
      }`}>
        <svg className="w-1/2 h-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </div>
    );
  }

  return (
    <div className={`${sizeClasses[size]} rounded-full overflow-hidden bg-gray-300`}>
      {user.avatar ? (
        <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
      ) : (
        <div className={`w-full h-full flex items-center justify-center font-medium ${
          isDarkMode ? 'bg-gray-600 text-white' : 'bg-gray-300 text-gray-700'
        }`}>
          {user.name.charAt(0).toUpperCase()}
        </div>
      )}
    </div>
  );
};

export default AssistantAvatar;