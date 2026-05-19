import React, { createContext, useContext, useEffect, useState } from 'react';

const ProfileContext = createContext();

export const ProfileProvider = ({ children }) => {
  const [profiles, setProfiles] = useState([]);
  const [activeProfile, setActiveProfile] = useState(null);

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/perfiles');
      const data = await res.json();

      setProfiles(data);

      const saved = localStorage.getItem('chefai_active_profile');

      if (saved) {
        setActiveProfile(JSON.parse(saved));
      }
    } catch (err) {
      console.error('Error cargando perfiles', err);
    }
  };

  const selectProfile = (profile) => {
    setActiveProfile(profile);

    if (profile) {
      localStorage.setItem(
        'chefai_active_profile',
        JSON.stringify(profile)
      );
    } else {
      localStorage.removeItem('chefai_active_profile');
    }
  };

  return (
    <ProfileContext.Provider
      value={{
        profiles,
        setProfiles,
        activeProfile,
        selectProfile,
        loadProfiles
      }}
    >
      {children}
    </ProfileContext.Provider>
  );
};

export const useProfile = () => useContext(ProfileContext);