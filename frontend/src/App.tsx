import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { Composer } from './components/Composer';
import { MCPView } from './components/MCPView';
import { MemoryView } from './components/MemoryView';
import { SystemView } from './components/SystemView';
import { SettingsView } from './components/SettingsView';
import type {
  Conversation,
  ChatMessage,
  SystemHealth,
  SystemStatus,
} from './types';
import {
  fetchHealth,
  fetchSystemStatus,
  fetchConversations,
  createConversation,
  fetchConversationDetails,
  sendMessage,
  deleteConversation,
} from './services/api';
import './styles/theme.css';
import './App.css';

export const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activeTab, setActiveTab] = useState<'chat' | 'mcp' | 'memory' | 'settings' | 'system'>('chat');
  const [loading, setLoading] = useState(false);

  // Poll health & system status
  useEffect(() => {
    const initTelemetry = async () => {
      try {
        const h = await fetchHealth();
        setHealth(h);
      } catch (err) {
        console.warn('Backend offline or starting up...', err);
      }
      try {
        const s = await fetchSystemStatus();
        setSystemStatus(s);
      } catch (err) {
        console.warn('Could not fetch initial status', err);
      }
    };
    initTelemetry();
  }, []);

  // Fetch conversations
  const loadConversations = async () => {
    try {
      const list = await fetchConversations();
      setConversations(list);
      if (list.length > 0 && !activeConvId) {
        setActiveConvId(list[0].id);
        loadConversationMessages(list[0].id);
      }
    } catch (err) {
      console.warn('Could not load conversations', err);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversationMessages = async (id: string) => {
    try {
      const details = await fetchConversationDetails(id);
      setMessages(details.messages);
    } catch (err) {
      console.error('Failed to load conversation details', err);
    }
  };

  const handleSelectConversation = (id: string) => {
    setActiveConvId(id);
    loadConversationMessages(id);
    setSidebarOpen(false);
  };

  const handleNewConversation = async () => {
    try {
      const newConv = await createConversation();
      setConversations((prev) => [newConv, ...prev]);
      setActiveConvId(newConv.id);
      setMessages([]);
      setActiveTab('chat');
      setSidebarOpen(false);
    } catch (err) {
      console.error('Failed to create conversation', err);
    }
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConvId === id) {
        setActiveConvId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Failed to delete conversation', err);
    }
  };

  const handleSendMessage = async (text: string) => {
    setLoading(true);
    let convId = activeConvId;

    try {
      if (!convId) {
        const newConv = await createConversation(text.slice(0, 30));
        setConversations((prev) => [newConv, ...prev]);
        setActiveConvId(newConv.id);
        convId = newConv.id;
      }

      // Add user message
      const userMsg = await sendMessage(convId, text, 'user');
      setMessages((prev) => [...prev, userMsg]);

      // Assistant acknowledgment in J0 (LLM integration occurs in J2)
      setTimeout(async () => {
        try {
          const assistantReply = await sendMessage(
            convId!,
            `JARVIS [Phase J0 Active]: Received "${text}". Core architecture, SQLite persistence, and API systems are operational. Ready for LLM brain integration in J2.`,
            'assistant'
          );
          setMessages((prev) => [...prev, assistantReply]);
        } catch (err) {
          console.error(err);
        } finally {
          setLoading(false);
        }
      }, 400);
    } catch (err) {
      console.error('Send message failed', err);
      setLoading(false);
    }
  };

  return (
    <div className="jarvis-app">
      <Header
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        health={health}
      />

      <div className="jarvis-body">
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          conversations={conversations}
          activeConversationId={activeConvId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          onDeleteConversation={handleDeleteConversation}
          systemStatus={systemStatus}
          activeTab={activeTab}
          onSelectTab={(tab) => {
            setActiveTab(tab);
            setSidebarOpen(false);
          }}
        />

        <main className="jarvis-main">
          {activeTab === 'chat' && (
            <div className="chat-view">
              <ChatArea
                messages={messages}
                onSelectSuggestion={(prompt) => handleSendMessage(prompt)}
              />
              <Composer
                onSendMessage={handleSendMessage}
                disabled={loading}
              />
            </div>
          )}

          {activeTab === 'mcp' && <MCPView />}
          {activeTab === 'memory' && <MemoryView />}
          {activeTab === 'system' && <SystemView />}
          {activeTab === 'settings' && <SettingsView />}
        </main>
      </div>
    </div>
  );
};

export default App;
