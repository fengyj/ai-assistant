import { type FC } from 'react';
import type { User } from '../types';

interface AssistantAvatarProps {
  user?: User | null;
  size?: 'sm' | 'md' | 'lg';
}

export const AssistantAvatar: FC<AssistantAvatarProps> = ({ 
  user, 
  size = 'md'
}) => {
  const avatarClass = `avatar size-${size}`;

  if (!user) {
    return (
      <div className={avatarClass}>
        <svg className="avatar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </div>
    );
  }

  return (
    <div className={avatarClass}>
      {user.avatar ? (
        <img src={user.avatar} alt={user.name} className="avatar-img" />
      ) : (
        <div className="avatar-fallback">
          {user.name.charAt(0).toUpperCase()}
        </div>
      )}
    </div>
  );
};

export default AssistantAvatar;