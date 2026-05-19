import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export const sendMessageToChef = async (
  message,
  condition,
  profileId
) => {
  try {
    const response = await axios.post(`${API_URL}/chat`, {
      mensaje: message,
      condicion: condition,
      perfil_id: profileId
    });

    return response.data;

  } catch (error) {
    console.error(
      'Error al enviar mensaje al servidor:',
      error
    );

    throw error;
  }
};