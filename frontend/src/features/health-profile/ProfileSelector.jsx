import React, { useState, useRef, useEffect } from 'react';
import { User, Plus, Pencil, Trash2, Heart } from 'lucide-react';
import { useProfile } from './ProfileContext';
import { ProfileModal } from './ProfileModal';
import { FavoritesPanel } from './FavoritesPanel';
import { deletePerfil } from '../../services/api/profileService';
import styles from './ProfileSelector.module.css';

export const ProfileSelector = () => {
  const { perfiles, perfilActivo, seleccionarPerfil, recargarPerfiles } = useProfile();
  const [open, setOpen] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editando, setEditando] = useState(null);
  const [showFavs, setShowFavs] = useState(false);
  const wrapperRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!confirm('¿Eliminar este perfil?')) return;
    await deletePerfil(id);
    await recargarPerfiles();
    if (perfilActivo?.id === id) seleccionarPerfil(null);
  };

  const handleEdit = (e, perfil) => {
    e.stopPropagation();
    setEditando(perfil);
    setShowModal(true);
    setOpen(false);
  };

  const handleSelect = (perfil) => {
    seleccionarPerfil(perfilActivo?.id === perfil.id ? null : perfil);
    setOpen(false);
  };

  return (
    <>
      <div className={styles.wrapper} ref={wrapperRef}>
        <button
          className={`${styles.trigger} ${perfilActivo ? styles.triggerActive : ''}`}
          onClick={() => setOpen(o => !o)}
          type="button"
        >
          <User size={14} />
          <span className={styles.triggerText}>
            {perfilActivo ? perfilActivo.nombre : 'Perfil'}
          </span>
          <svg className={`${styles.caret} ${open ? styles.caretUp : ''}`}
            width="10" height="6" viewBox="0 0 10 6" fill="none">
            <path d="M1 1l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </button>

        {open && (
          <div className={styles.panel}>
            <div className={styles.panelHeader}>
              <span className={styles.panelTitle}>Perfiles</span>
              <button
                className={styles.newBtn}
                onClick={() => { setEditando(null); setShowModal(true); setOpen(false); }}
                type="button"
              >
                <Plus size={12} /> Nuevo
              </button>
            </div>

            {perfiles.length === 0 ? (
              <p className={styles.empty}>Sin perfiles aún.<br/>Crea uno para guardar tus preferencias.</p>
            ) : (
              <div className={styles.list}>
                {/* Opción sin perfil */}
                <div
                  className={`${styles.item} ${!perfilActivo ? styles.itemActive : ''}`}
                  onClick={() => { seleccionarPerfil(null); setOpen(false); }}
                >
                  <span className={styles.itemAvatar}>👤</span>
                  <span className={styles.itemName}>Sin perfil</span>
                </div>

                {perfiles.map(p => (
                  <div
                    key={p.id}
                    className={`${styles.item} ${perfilActivo?.id === p.id ? styles.itemActive : ''}`}
                    onClick={() => handleSelect(p)}
                  >
                    <span className={styles.itemAvatar}>
                      {p.nombre.charAt(0).toUpperCase()}
                    </span>
                    <div className={styles.itemInfo}>
                      <span className={styles.itemName}>{p.nombre}</span>
                      {p.condiciones_lista?.length > 0 && (
                        <span className={styles.itemSub}>
                          {p.condiciones_lista.length} restricción{p.condiciones_lista.length > 1 ? 'es' : ''}
                        </span>
                      )}
                    </div>
                    <div className={styles.itemActions}>
                      <button
                        className={styles.actionBtn}
                        onClick={(e) => handleEdit(e, p)}
                        title="Editar"
                      >
                        <Pencil size={12} />
                      </button>
                      <button
                        className={`${styles.actionBtn} ${styles.actionDanger}`}
                        onClick={(e) => handleDelete(e, p.id)}
                        title="Eliminar"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Botón ver favoritos */}
            {perfilActivo && (
              <button
                className={styles.favsBtn}
                onClick={() => { setShowFavs(true); setOpen(false); }}
                type="button"
              >
                <Heart size={13} /> Ver recetas favoritas de {perfilActivo.nombre}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Modals */}
      {showModal && (
        <ProfileModal
          perfil={editando}
          onClose={() => { setShowModal(false); setEditando(null); }}
        />
      )}
      {showFavs && perfilActivo && (
        <FavoritesPanel
          perfilId={perfilActivo.id}
          perfilNombre={perfilActivo.nombre}
          onClose={() => setShowFavs(false)}
        />
      )}
    </>
  );
};