import React, { useState } from 'react';
import { Send } from 'lucide-react';
import styles from './ChatInput.module.css';

export const ChatInput = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className={styles.inputBar}>
      <form onSubmit={handleSubmit} className={styles.inputPill}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Escribe los ingredientes que tienes..."
          disabled={disabled}
        />
        <button 
          type="submit" 
          className={styles.sendBtn}
          disabled={!message.trim() || disabled}
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  );
};
