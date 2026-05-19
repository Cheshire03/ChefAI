import React, { useState } from 'react';
import { Heart } from 'lucide-react';
import { useProfile } from '../health-profile/ProfileContext';
import { addLike, removeLike } from '../../services/api/profileService';
import styles from './MessageBubble.module.css';
import mindyLogo from '../../assets/mindy-logo.png';


export const MessageBubble = ({ text, sender, time, recipeId, recipeNombre, recipeIngredientes, yaLiked }) => {
  const isUser = sender === 'user';
  const isBot = sender === 'bot';
  const { perfilActivo } = useProfile();

  const [liked, setLiked] = useState(yaLiked || false);
  const [likeLoading, setLikeLoading] = useState(false);

  const handleLike = async () => {
    if (!perfilActivo || !recipeId || likeLoading) return;
    setLikeLoading(true);
    try {
      if (liked) {
        await removeLike(perfilActivo.id, recipeId);
        setLiked(false);
      } else {
        await addLike(perfilActivo.id, recipeId, recipeNombre || '', recipeIngredientes || []);
        setLiked(true);
      }
    } catch (e) {
      console.error('Error al manejar like:', e);
    } finally {
      setLikeLoading(false);
    }
  };

  const renderText = (text) => {
    if (!text) return null;
    return text.split('\n').map((line, i) => {
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
          <img src={mindyLogo} alt="Mindy" className={styles.msgAvImg} />

        </div>
      )}

      <div className={styles.bubbleWrapper}>
        <div className={`${styles.bubble} ${isUser ? styles.userBubble : styles.botBubble}`}>
          {renderText(text)}
          {time && <span className={styles.ts}>{time}</span>}
        </div>

        {/* Botón like — solo en mensajes del bot con receta y perfil activo */}
        {isBot && recipeId && perfilActivo && (
          <button
            className={`${styles.likeBtn} ${liked ? styles.likeBtnActive : ''}`}
            onClick={handleLike}
            disabled={likeLoading}
            title={liked ? 'Quitar de favoritos' : 'Guardar en favoritos'}
          >
            <Heart
              size={13}
              fill={liked ? 'currentColor' : 'none'}
              strokeWidth={liked ? 0 : 2}
            />
            <span>{liked ? 'Guardada' : 'Me gusta'}</span>
          </button>
        )}

        {/* Hint si no hay perfil activo */}
        {isBot && recipeId && !perfilActivo && (
          <p className={styles.noProfileHint}>
            Selecciona un perfil para guardar favoritos
          </p>
        )}
      </div>
    </div>
  );
};