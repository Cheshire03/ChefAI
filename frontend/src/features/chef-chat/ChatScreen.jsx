import React, { useState, useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { ConditionSelector } from '../health-profile/ConditionSelector';
import { Spinner } from '../../shared/ui/Spinner';
import { sendMessageToChef } from '../../services/api/chatService';
import styles from './ChatScreen.module.css';
import { ProfileSelector } from '../profiles/ProfileSelector';
import { useProfile } from '../../context/ProfileContext';
import { ProfileModal } from '../profiles/ProfileModal';

export const ChatScreen = () => {
  const [profileModalOpen, setProfileModalOpen] = useState(false);
  const { activeProfile } = useProfile();
  useEffect(() => {
    if (activeProfile?.condiciones) {
      setCondition(activeProfile.condiciones);
    } else {
      setCondition('');
    }
  }, [activeProfile]);
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
      const response = await sendMessageToChef(
        text,
        condition,
        activeProfile?.id
      );
      const botMsg = {
        id: Date.now() + 1,
        sender: 'bot',
        text: response.respuesta,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        recipeId: response.receta_id
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      const errorMsg = {
        id: Date.now() + 1,
        sender: 'bot',
        text: 'Lo siento, tuve un problema de conexión con el motor local. Asegúrate de que el servidor Flask esté corriendo.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className={styles.screen}>
        {/* Navbar */}
        <div className={styles.navbar}>
          <div className={styles.navBrand}>
            <div className={styles.navAv}>
              <span>👩‍🍳</span>
              <div className={styles.onlineDot}></div>
            </div>

            <div>
              <div className={styles.navName}>Mindy</div>
              <div className={styles.navSub}>
                Tu chef IA · En línea
              </div>
            </div>
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}
          >
            <ProfileSelector />

            <button
              onClick={() => setProfileModalOpen(true)}
              style={{
                width: '34px',
                height: '34px',
                borderRadius: '50%',
                border: 'none',
                background: 'var(--or)',
                color: 'white',
                fontSize: '20px',
                cursor: 'pointer'
              }}
            >
              +
            </button>

            <ConditionSelector
              condition={condition}
              setCondition={setCondition}
            />
          </div>
        </div>

        {/* Chat Area */}
        <div
          className="scroll-area"
          ref={scrollRef}
          style={{ padding: '14px 14px 0' }}
        >
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
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
        />
      </div>

      <ProfileModal
        open={profileModalOpen}
        onClose={() => setProfileModalOpen(false)}
      />
    </>
  );
};
