import React from 'react';

interface AvatarProps {
  src?: string;
  alt?: string;
  size?: number;
  className?: string;
}

/**
 * 通用用户头像组件，支持自定义大小和图片
 */
const Avatar: React.FC<AvatarProps> = ({ src, alt = 'avatar', size = 32, className = '' }) => {
  return (
    <img
      src={src || '/public/default-avatar.svg'}
      alt={alt}
      width={size}
      height={size}
      className={`rounded-full object-cover bg-gray-200 dark:bg-gray-700 ${className}`}
      loading="lazy"
    />
  );
};

export default Avatar;
