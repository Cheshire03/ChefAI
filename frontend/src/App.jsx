import React from 'react';
import { ChatScreen } from './features/chef-chat/ChatScreen';
import { ProfileProvider } from './features/health-profile/ProfileContext';

function App() {
  return (
    <ProfileProvider>
      <ChatScreen />
    </ProfileProvider>
  );
}

export default App;
