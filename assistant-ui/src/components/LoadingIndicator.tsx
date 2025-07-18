import { type FC } from 'react';

interface LoadingIndicatorProps {
  isDarkMode?: boolean;
}

export const LoadingIndicator: FC<LoadingIndicatorProps> = ({ isDarkMode = false }) => {
  return (
    <div className="flex justify-start">
      <div className={`max-w-xl px-4 py-3 rounded-lg ${
        isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
      } shadow-sm`}>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
          <span className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            AI is thinking...
          </span>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;