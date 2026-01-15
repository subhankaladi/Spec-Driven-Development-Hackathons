/**
 * Message display component
 * Shows individual messages with appropriate styling based on role and status
 */

import React from 'react';
import { ChatMessage } from '../../types/chatTypes';

interface MessageDisplayProps {
  message: ChatMessage;
}

const MessageDisplay: React.FC<MessageDisplayProps> = ({ message }) => {
  const getMessageClassName = () => {
    let baseClass = 'message';
    baseClass += ` message-${message.role}`;
    baseClass += ` message-status-${message.status}`;
    return baseClass;
  };

  const getStatusIndicator = () => {
    switch (message.status) {
      case 'sending':
        return <span className="status-indicator sending">Sending...</span>;
      case 'error':
        return <span className="status-indicator error">Error</span>;
      case 'confirmed':
        return <span className="status-indicator confirmed">✓</span>;
      default:
        return null;
    }
  };

  return (
    <div className={getMessageClassName()}>
      <div className="message-header">
        <span className="message-role">{message.role === 'user' ? 'You' : 'Assistant'}</span>
        <span className="message-timestamp">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
        {getStatusIndicator()}
      </div>
      <div className="message-content">
        {message.content}
      </div>
    </div>
  );
};

export default MessageDisplay;