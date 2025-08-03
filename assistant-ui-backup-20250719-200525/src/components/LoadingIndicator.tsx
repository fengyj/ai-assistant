import { type FC } from 'react';

export const LoadingIndicator: FC = () => {
  return (
    <div className="loading-indicator">
      <div className="loading-bubble">
        <div className="loading-content">
          <div className="loading-dot"></div>
          <div className="loading-dot"></div>
          <div className="loading-dot"></div>
          <span className="loading-text">AI is thinking...</span>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;