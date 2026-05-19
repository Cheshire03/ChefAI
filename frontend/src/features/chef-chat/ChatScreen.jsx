import React, { useState, useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { ConditionSelector } from '../health-profile/ConditionSelector';
import { ProfileSelector } from '../health-profile/ProfileSelector';
import { Spinner } from '../../shared/ui/Spinner';
import { useProfile } from '../health-profile/ProfileContext';
import { sendMessageToChef } from '../../services/api/chatService';
import styles from './ChatScreen.module.css';
import mindyLogo from '../../assets/mindy-logo.png';


export const ChatScreen = () => {
  const { perfilActivo } = useProfile();
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: '¡Hola! Soy Mindy, tu chef personal con IA. Dime qué ingredientes tienes en tu nevera y te sugeriré algo delicioso.',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [condition, setCondition] = useState('');
  const scrollRef = useRef(null);

  // Sincronizar condiciones con el perfil activo
  useEffect(() => {
    if (perfilActivo) {
      setCondition(perfilActivo.condiciones || '');
    } else {
      setCondition('');
    }
  }, [perfilActivo]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSendMessage = async (text) => {
    const newUserMsg = {
      id: Date.now(),
      sender: 'user',
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, newUserMsg]);
    setIsLoading(true);

    try {
      const response = await sendMessageToChef(text, condition, perfilActivo?.id);
      const botMsg = {
        id: Date.now() + 1,
        sender: 'bot',
        text: response.respuesta,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        recipeId: response.receta_id,
        recipeNombre: response.receta_nombre,
        recipeIngredientes: response.receta_ingredientes,
        yaLiked: response.ya_tiene_like || false,
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'bot',
        text: 'Lo siento, tuve un problema de conexión. Asegúrate de que el servidor Flask esté corriendo.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.screen}>
      {/* Navbar */}
      <div className={styles.navbar}>
        <div className={styles.navBrand}>
          <div className={styles.navAv}>
              <img src={mindyLogo} alt="Mindy" className={styles.navAvImg} />

            <div className={styles.onlineDot}></div>
          </div>
          <div>
            <div className={styles.navName}>Mindy</div>
            <div className={styles.navSub}>
              {perfilActivo
                ? `Hola, ${perfilActivo.nombre} 👋`
                : 'Tu chef IA · En línea'}
            </div>
          </div>
        </div>

        <div className={styles.navControls}>
          <ConditionSelector condition={condition} setCondition={setCondition} />
          <ProfileSelector />
        </div>
      </div>

      {/* Chat Area */}
      <div className="scroll-area" ref={scrollRef} style={{ padding: '14px 14px 0' }}>
        <div className={styles.dateChip}>Hoy</div>

        {messages.map(msg => (
          <MessageBubble key={msg.id} {...msg} />
        ))}

        {isLoading && (
          <div style={{ marginBottom: '10px' }}>
            <Spinner />
          </div>
        )}
      </div>

      {/* Input */}
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
};