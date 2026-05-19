import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { createPerfil, updatePerfil } from '../../services/api/profileService';
import { useProfile } from './ProfileContext';
import styles from './ProfileModal.module.css';

const CONDITIONS = [
  { value: "diabetes",             label: "Diabetes" },
  { value: "hipertension",         label: "Hipertensión" },
  { value: "celiaquia,sin_gluten", label: "Celiaquía / Sin gluten" },
  { value: "resistencia_insulina", label: "Res. insulina" },
  { value: "colesterol_alto",      label: "Colesterol alto" },
  { value: "vegetariano",          label: "Vegetariano" },
  { value: "vegano",               label: "Vegano" },
  { value: "alto_proteina",        label: "Alto proteína" },
  { value: "bajo_sodio",           label: "Bajo sodio" },
  { value: "bajo_calorias",        label: "Bajo calorías" },
];

const ALERGIAS = [
  { value: "gluten",    label: "Gluten" },
  { value: "lactosa",   label: "Lactosa" },
  { value: "mariscos",  label: "Mariscos" },
  { value: "nueces",    label: "Nueces" },
  { value: "soya",      label: "Soya" },
  { value: "huevo",     label: "Huevo" },
];

const COCINAS = [
  { value: "",          label: "Sin preferencia" },
  { value: "mexicana",  label: "🇲🇽 Mexicana" },
  { value: "italiana",  label: "🇮🇹 Italiana" },
  { value: "asiatica",  label: "🥢 Asiática" },
  { value: "mediterranea", label: "🫒 Mediterránea" },
];

const TIEMPOS = [
  { value: "",       label: "Sin preferencia" },
  { value: "rapido", label: "⚡ Rápido (<20 min)" },
  { value: "normal", label: "🕐 Normal (20-45 min)" },
  { value: "largo",  label: "🍲 Elaborado (>45 min)" },
];

const DIFICULTADES = [
  { value: "",       label: "Sin preferencia" },
  { value: "fácil",  label: "🟢 Fácil" },
  { value: "media",  label: "🟡 Media" },
  { value: "difícil", label: "🔴 Difícil" },
];

const EMPTY_FORM = {
  nombre: '',
  condiciones: new Set(),
  alergias: new Set(),
  cocina: '',
  tiempo_max: '',
  dificultad: '',
};

export const ProfileModal = ({ perfil, onClose }) => {
  const { recargarPerfiles } = useProfile();
  const [form, setForm] = useState(EMPTY_FORM);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const isEditing = !!perfil;

  useEffect(() => {
    if (perfil) {
      setForm({
        nombre: perfil.nombre,
        condiciones: new Set(perfil.condiciones ? perfil.condiciones.split(',').filter(Boolean) : []),
        alergias: new Set(perfil.alergias || []),
        cocina: perfil.cocina || '',
        tiempo_max: perfil.tiempo_max || '',
        dificultad: perfil.dificultad || '',
      });
    }
  }, [perfil]);

  const toggleSet = (key, value) => {
    setForm(prev => {
      const next = new Set(prev[key]);
      next.has(value) ? next.delete(value) : next.add(value);
      return { ...prev, [key]: next };
    });
  };

  const handleSubmit = async () => {
    if (!form.nombre.trim()) {
      setError('El nombre es obligatorio');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const payload = {
        nombre: form.nombre.trim(),
        condiciones: [...form.condiciones].join(','),
        alergias: [...form.alergias],
        cocina: form.cocina,
        tiempo_max: form.tiempo_max,
        dificultad: form.dificultad,
      };
      if (isEditing) {
        await updatePerfil(perfil.id, payload);
      } else {
        await createPerfil(payload);
      }
      await recargarPerfiles();
      onClose();
    } catch (e) {
      setError('Error al guardar el perfil. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className={styles.header}>
          <span className={styles.title}>
            {isEditing ? '✏️ Editar perfil' : '👤 Nuevo perfil'}
          </span>
          <button className={styles.closeBtn} onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className={styles.body}>

          {/* Nombre */}
          <div className={styles.field}>
            <label className={styles.label}>Nombre del perfil</label>
            <input
              className={styles.input}
              placeholder="Ej: Mamá, Papá, Yo..."
              value={form.nombre}
              onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))}
              maxLength={40}
            />
          </div>

          {/* Condiciones */}
          <div className={styles.field}>
            <label className={styles.label}>Condiciones médicas</label>
            <div className={styles.chips}>
              {CONDITIONS.map(c => (
                <button
                  key={c.value}
                  type="button"
                  className={`${styles.chip} ${form.condiciones.has(c.value) ? styles.chipActive : ''}`}
                  onClick={() => toggleSet('condiciones', c.value)}
                >
                  {form.condiciones.has(c.value) && <span>✓ </span>}
                  {c.label}
                </button>
              ))}
            </div>
          </div>

          {/* Alergias */}
          <div className={styles.field}>
            <label className={styles.label}>Alergias</label>
            <div className={styles.chips}>
              {ALERGIAS.map(a => (
                <button
                  key={a.value}
                  type="button"
                  className={`${styles.chip} ${form.alergias.has(a.value) ? styles.chipDanger : ''}`}
                  onClick={() => toggleSet('alergias', a.value)}
                >
                  {form.alergias.has(a.value) && <span>✓ </span>}
                  {a.label}
                </button>
              ))}
            </div>
          </div>

          {/* Preferencias */}
          <div className={styles.field}>
            <label className={styles.label}>Preferencias</label>
            <div className={styles.selects}>
              <select
                className={styles.select}
                value={form.cocina}
                onChange={e => setForm(f => ({ ...f, cocina: e.target.value }))}
              >
                {COCINAS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
              <select
                className={styles.select}
                value={form.tiempo_max}
                onChange={e => setForm(f => ({ ...f, tiempo_max: e.target.value }))}
              >
                {TIEMPOS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
              <select
                className={styles.select}
                value={form.dificultad}
                onChange={e => setForm(f => ({ ...f, dificultad: e.target.value }))}
              >
                {DIFICULTADES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
          </div>

          {error && <p className={styles.error}>{error}</p>}
        </div>

        {/* Footer */}
        <div className={styles.footer}>
          <button className={styles.cancelBtn} onClick={onClose} disabled={loading}>
            Cancelar
          </button>
          <button className={styles.saveBtn} onClick={handleSubmit} disabled={loading}>
            {loading ? 'Guardando...' : isEditing ? 'Guardar cambios' : 'Crear perfil'}
          </button>
        </div>

      </div>
    </div>
  );
};