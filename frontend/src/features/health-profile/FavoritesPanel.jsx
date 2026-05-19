import React, { useEffect, useState } from 'react';
import { X, Heart } from 'lucide-react';
import { getLikes, removeLike } from '../../services/api/profileService';
import styles from './FavoritesPanel.module.css';

export const FavoritesPanel = ({ perfilId, perfilNombre, onClose }) => {
  const [likes, setLikes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cargar = async () => {
      try {
        const data = await getLikes(perfilId);
        setLikes(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    cargar();
  }, [perfilId]);

  const handleRemove = async (recetaId) => {
    await removeLike(perfilId, recetaId);
    setLikes(prev => prev.filter(l => l.receta_id !== recetaId));
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.panel} onClick={e => e.stopPropagation()}>

        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <Heart size={16} fill="currentColor" />
            <span className={styles.title}>Favoritos de {perfilNombre}</span>
          </div>
          <button className={styles.closeBtn} onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className={styles.body}>
          {loading ? (
            <p className={styles.empty}>Cargando...</p>
          ) : likes.length === 0 ? (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>❤️</span>
              <p>Aún no hay recetas favoritas.</p>
              <p className={styles.emptyHint}>Dale ❤️ a las recetas que te recomiende Mindy.</p>
            </div>
          ) : (
            <div className={styles.list}>
              {likes.map(like => (
                <div key={like.receta_id} className={styles.card}>
                  <div className={styles.cardInfo}>
                    <span className={styles.cardName}>{like.nombre}</span>
                    {like.ingredientes && (
                      <span className={styles.cardIngs}>
                        {like.ingredientes.split(',').slice(0, 4).join(', ')}
                        {like.ingredientes.split(',').length > 4 ? '...' : ''}
                      </span>
                    )}
                    <span className={styles.cardDate}>
                      {new Date(like.guardado_en).toLocaleDateString('es-MX', {
                        day: 'numeric', month: 'short'
                      })}
                    </span>
                  </div>
                  <button
                    className={styles.removeBtn}
                    onClick={() => handleRemove(like.receta_id)}
                    title="Quitar de favoritos"
                  >
                    <Heart size={14} fill="currentColor" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
};