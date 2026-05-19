const BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// ─────────────────────────────────────────────
// PERFILES
// ─────────────────────────────────────────────

export const getPerfiles = async () => {
  const res = await fetch(`${BASE}/api/perfiles`);
  if (!res.ok) throw new Error('Error al cargar perfiles');
  return res.json();
};

export const createPerfil = async (datos) => {
  const res = await fetch(`${BASE}/api/perfiles`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  });
  if (!res.ok) throw new Error('Error al crear perfil');
  return res.json();
};

export const updatePerfil = async (id, datos) => {
  const res = await fetch(`${BASE}/api/perfiles/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  });
  if (!res.ok) throw new Error('Error al actualizar perfil');
  return res.json();
};

export const deletePerfil = async (id) => {
  const res = await fetch(`${BASE}/api/perfiles/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Error al eliminar perfil');
  return res.json();
};

// ─────────────────────────────────────────────
// LIKES
// ─────────────────────────────────────────────

export const getLikes = async (perfilId) => {
  const res = await fetch(`${BASE}/api/perfiles/${perfilId}/likes`);
  if (!res.ok) throw new Error('Error al cargar favoritos');
  return res.json();
};

export const addLike = async (perfilId, recetaId, nombre, ingredientes) => {
  const res = await fetch(`${BASE}/api/perfiles/${perfilId}/likes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ receta_id: recetaId, nombre, ingredientes }),
  });
  if (!res.ok) throw new Error('Error al dar like');
  return res.json();
};

export const removeLike = async (perfilId, recetaId) => {
  const res = await fetch(`${BASE}/api/perfiles/${perfilId}/likes/${recetaId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Error al quitar like');
  return res.json();
};