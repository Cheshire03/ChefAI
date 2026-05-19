const BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const sendMessageToChef = async (mensaje, condicion = '', perfilId = null) => {
  const body = { mensaje, condicion };
  if (perfilId) body.perfil_id = perfilId;

  const res = await fetch(`${BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Error en el servidor');
  }

  return res.json();
};