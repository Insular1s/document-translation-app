import React from 'react';

interface ProgressIndicatorProps {
  message: string;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ message }) => {
  return (
    <div className="progress-indicator">
      <div className="spinner"></div>
      <h3>{message}</h3>
      <p>Please wait while we process your document...</p>
    </div>
  );
};

export default ProgressIndicator;