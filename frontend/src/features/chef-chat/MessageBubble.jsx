import React from 'react';
import styles from './MessageBubble.module.css';

export const MessageBubble = ({ text, sender, time, recipeId }) => {
  const isUser = sender === 'user';
  
  // Función para renderizar Markdown simple (negritas devueltas por Gemini)
  const renderText = (text) => {
    // Si no hay texto, retornar nulo
    if (!text) return null;
    
    // Separamos por líneas para respetar los \n
    return text.split('\n').map((line, i) => {
      // Reemplazamos **texto** por <strong>texto</strong> usando react de forma segura
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <React.Fragment key={i}>
          {parts.map((part, j) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return <strong key={j}>{part.slice(2, -2)}</strong>;
            }
            return <span key={j}>{part}</span>;
          })}
          {i < text.split('\n').length - 1 && <br />}
        </React.Fragment>
      );
    });
  };

  return (
    <div className={`${styles.msgRow} ${isUser ? styles.userRow : styles.botRow}`}>
      {!isUser && (
        <div className={styles.msgAv}>
          <span>🤖</span>
        </div>
      )}
      <div className={`${styles.bubble} ${isUser ? styles.userBubble : styles.botBubble}`}>
        {renderText(text)}
        {time && <span className={styles.ts}>{time}</span>}
      </div>
    </div>
  );
};
