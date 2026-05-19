import React from 'react';
import { useProfile } from '../../context/ProfileContext';
import styles from './ProfileSelector.module.css';

export const ProfileSelector = () => {
  const {
    profiles,
    activeProfile,
    selectProfile
  } = useProfile();

  return (
    <select
      className={styles.select}
      value={activeProfile?.id || ''}
      onChange={(e) => {
        const selected = profiles.find(
          p => p.id === Number(e.target.value)
        );

        selectProfile(selected || null);
      }}
    >
      <option value="">Invitado</option>

      {profiles.map(profile => (
        <option
          key={profile.id}
          value={profile.id}
        >
          {profile.nombre}
        </option>
      ))}
    </select>
  );
};  