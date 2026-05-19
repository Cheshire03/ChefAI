import React, { useState, useRef, useEffect } from 'react';
import styles from './ConditionSelector.module.css';

const CONDITIONS = [
  { value: "diabetes",             label: "Diabetes",          desc: "Bajo en azúcar" },
  { value: "hipertension",         label: "Hipertensión",      desc: "Bajo en sodio" },
  { value: "celiaquia",            label: "Celiaquía",         desc: "Sin gluten" },
  { value: "resistencia_insulina", label: "Res. insulina",     desc: "Control glucémico" },
  { value: "colesterol_alto",      label: "Colesterol alto",   desc: "Bajo en grasas" },
  { value: "vegetariano",          label: "Vegetariano",       desc: "Sin carne" },
  { value: "vegano",               label: "Vegano",            desc: "Sin productos animales" },
  { value: "alto_proteina",        label: "Alto proteína",     desc: "Dieta proteica" },
  { value: "bajo_sodio",           label: "Bajo sodio",        desc: "Hipertensión / riñón" },
  { value: "bajo_calorias",        label: "Bajo calorías",     desc: "Control de peso" },
  { value: "sin_lactosa",          label: "Sin lactosa",       desc: "Intolerancia láctea" },
];

export const ConditionSelector = ({ condition, setCondition }) => {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState(() =>
    new Set(condition ? condition.split(',').filter(Boolean) : [])
  );
  const wrapperRef = useRef(null);

  // Sincronizar cuando condition cambia desde afuera (ej: al seleccionar un perfil)
  useEffect(() => {
    setSelected(new Set(condition ? condition.split(',').filter(Boolean) : []));
  }, [condition]);

  // Cerrar al click fuera
  useEffect(() => {
    const handler = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const toggle = (value) => {
    const next = new Set(selected);
    next.has(value) ? next.delete(value) : next.add(value);
    setSelected(next);
    setCondition([...next].join(','));
  };

  const clear = (e) => {
    e.stopPropagation();
    const empty = new Set();
    setSelected(empty);
    setCondition('');
  };

  const activeLabels = [...selected]
    .map(v => CONDITIONS.find(c => c.value === v)?.label)
    .filter(Boolean);

  const triggerText = selected.size === 0
    ? 'Sin restricciones'
    : selected.size === 1
      ? activeLabels[0]
      : `${activeLabels[0]} +${selected.size - 1}`;

  return (
    <div className={styles.wrapper} ref={wrapperRef}>
      <button
        className={`${styles.trigger} ${open ? styles.triggerOpen : ''}`}
        onClick={() => setOpen(o => !o)}
        type="button"
      >
        <span className={styles.triggerText}>{triggerText}</span>
        {selected.size > 0 && (
          <>
            <span className={styles.badge}>{selected.size}</span>
            <span
              className={styles.clearX}
              onClick={clear}
              role="button"
              aria-label="Limpiar"
            >×</span>
          </>
        )}
        <svg
          className={`${styles.caret} ${open ? styles.caretUp : ''}`}
          width="10" height="6" viewBox="0 0 10 6" fill="none"
        >
          <path d="M1 1l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      </button>

      {open && (
        <div className={styles.panel}>
          <div className={styles.panelHeader}>
            <span className={styles.panelTitle}>Perfil de salud</span>
            {selected.size > 0 && (
              <button className={styles.clearAll} onClick={clear} type="button">
                Limpiar
              </button>
            )}
          </div>

          <div className={styles.chips}>
            {CONDITIONS.map(c => {
              const isActive = selected.has(c.value);
              return (
                <button
                  key={c.value}
                  className={`${styles.chip} ${isActive ? styles.chipActive : ''}`}
                  onClick={() => toggle(c.value)}
                  title={c.desc}
                  type="button"
                >
                  {isActive && <span className={styles.check}>✓</span>}
                  {c.label}
                </button>
              );
            })}
          </div>

          {selected.size > 0 && (
            <div className={styles.preview}>
              {activeLabels.join(' · ')}
            </div>
          )}
        </div>
      )}
    </div>
  );
};