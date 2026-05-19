import React, { useState } from 'react';
import { useProfile } from '../../context/ProfileContext';
import { CONDITIONS } from '../health-profile/conditionsData';
import styles from './ProfileModal.module.css';

const ALLERGIES = [
  'gluten',
  'lactosa',
  'mariscos',
  'nueces',
  'soya',
  'huevo'
];

export const ProfileModal = ({ open, onClose }) => {

  const { loadProfiles } = useProfile();

  const [name, setName] = useState('');
  const [selected, setSelected] = useState(new Set());
  const [allergies, setAllergies] = useState(new Set());

  const [loading, setLoading] = useState(false);

  const [cocina, setCocina] = useState('');
  const [tiempoMax, setTiempoMax] = useState('');
  const [dificultad, setDificultad] = useState('');

  if (!open) return null;

  const toggle = (value) => {

    const next = new Set(selected);

    next.has(value)
      ? next.delete(value)
      : next.add(value);

    setSelected(next);
  };

  const toggleAllergy = (value) => {

    const next = new Set(allergies);

    next.has(value)
      ? next.delete(value)
      : next.add(value);

    setAllergies(next);
  };

  const handleSave = async () => {

    if (!name.trim()) return;

    setLoading(true);

    try {

      await fetch('http://localhost:5000/api/perfiles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },

        body: JSON.stringify({
          nombre: name,
          condiciones: [...selected].join(','),
          alergias: [...allergies],
          cocina,
          tiempo_max: tiempoMax,
          dificultad
        })
      });

      await loadProfiles();

      setName('');
      setSelected(new Set());
      setAllergies(new Set());

      setCocina('');
      setTiempoMax('');
      setDificultad('');

      onClose();

    } catch (err) {

      console.error(err);

    } finally {

      setLoading(false);
    }
  };

  return (
    <div className={styles.overlay}>

      <div className={styles.modal}>

        <div className={styles.header}>
          <h2>Nuevo perfil</h2>

          <button onClick={onClose}>
            ✕
          </button>
        </div>

        <input
          type="text"
          placeholder="Nombre del perfil"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className={styles.input}
        />

        {/* Condiciones */}
        <div className={styles.section}>

          <label>Condiciones</label>

          <div className={styles.conditions}>

            {CONDITIONS.map(c => {

              const active = selected.has(c.value);

              return (
                <button
                  key={c.value}
                  type="button"
                  onClick={() => toggle(c.value)}
                  className={`${styles.chip} ${active ? styles.active : ''}`}
                >
                  {c.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Cocina */}
        <div className={styles.section}>

          <label>Tipo de cocina favorita</label>

          <select
            value={cocina}
            onChange={(e) => setCocina(e.target.value)}
          >
            <option value="">Sin preferencia</option>
            <option value="mexicana">Mexicana</option>
            <option value="internacional">Internacional</option>
            <option value="mediterránea">Mediterránea</option>
            <option value="italiana">Italiana</option>
            <option value="española">Española</option>
            <option value="asiática">Asiática</option>
            <option value="fusion">Fusión</option>
          </select>
        </div>

        {/* Tiempo */}
        <div className={styles.section}>

          <label>Tiempo preferido</label>

          <select
            value={tiempoMax}
            onChange={(e) => setTiempoMax(e.target.value)}
          >
            <option value="">Sin preferencia</option>
            <option value="rápido">Rápido (&lt;20 min)</option>
            <option value="normal">Normal</option>
            <option value="elaborado">Elaborado</option>
          </select>
        </div>

        {/* Dificultad */}
        <div className={styles.section}>

          <label>Dificultad preferida</label>

          <select
            value={dificultad}
            onChange={(e) => setDificultad(e.target.value)}
          >
            <option value="">Sin preferencia</option>
            <option value="fácil">Fácil</option>
            <option value="media">Media</option>
            <option value="difícil">Difícil</option>
          </select>
        </div>

        {/* Alergias */}
        <div className={styles.section}>

          <label>Alergias</label>

          <div className={styles.conditions}>

            {ALLERGIES.map(a => {

              const active = allergies.has(a);

              return (
                <button
                  key={a}
                  type="button"
                  onClick={() => toggleAllergy(a)}
                  className={`${styles.chip} ${active ? styles.active : ''}`}
                >
                  {a}
                </button>
              );
            })}
          </div>
        </div>

        <button
          onClick={handleSave}
          disabled={loading}
          className={styles.saveBtn}
        >
          {loading ? 'Guardando...' : 'Guardar perfil'}
        </button>

      </div>
    </div>
  );
};