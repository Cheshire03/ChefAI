import React, { createContext, useContext, useState, useEffect } from 'react';
import { getPerfiles } from '../../services/api/profileService';

const ProfileContext = createContext(null);

export const ProfileProvider = ({ children }) => {
  const [perfiles, setPerfiles] = useState([]);
  const [perfilActivo, setPerfilActivo] = useState(null);
  const [loading, setLoading] = useState(true);

  const cargarPerfiles = async () => {
    try {
      const data = await getPerfiles();
      setPerfiles(data);
      // Restaurar perfil activo desde localStorage
      const savedId = localStorage.getItem('chefai_perfil_activo');
      if (savedId) {
        const encontrado = data.find(p => p.id === parseInt(savedId));
        if (encontrado) setPerfilActivo(encontrado);
      }
    } catch (e) {
      console.error('Error cargando perfiles:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargarPerfiles(); }, []);

  const seleccionarPerfil = (perfil) => {
    setPerfilActivo(perfil);
    if (perfil) {
      localStorage.setItem('chefai_perfil_activo', perfil.id);
    } else {
      localStorage.removeItem('chefai_perfil_activo');
    }
  };

  return (
    <ProfileContext.Provider value={{
      perfiles,
      perfilActivo,
      loading,
      seleccionarPerfil,
      recargarPerfiles: cargarPerfiles,
    }}>
      {children}
    </ProfileContext.Provider>
  );
};

export const useProfile = () => {
  const ctx = useContext(ProfileContext);
  if (!ctx) throw new Error('useProfile debe usarse dentro de ProfileProvider');
  return ctx;
};