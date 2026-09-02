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
  streamChat,
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

      // 1. Append user message locally
      const userMsg: ChatMessage = {
        conversation_id: convId,
        role: 'user',
        content: text,
        created_at: new Date().toISOString(),
      };

      // 2. Append empty assistant placeholder
      const assistantPlaceholder: ChatMessage = {
        conversation_id: convId,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMsg, assistantPlaceholder]);

      // 3. Stream tokens progressively from NVIDIA / active provider
      await streamChat(
        convId,
        text,
        (token) => {
          setMessages((prev) => {
            const updated = [...prev];
            const lastIdx = updated.length - 1;
            if (lastIdx >= 0 && updated[lastIdx].role === 'assistant') {
              updated[lastIdx] = {
                ...updated[lastIdx],
                content: updated[lastIdx].content + token,
              };
            }
            return updated;
          });
        },
        () => {
          setLoading(false);
          loadConversations();
        },
        (errMsg) => {
          setMessages((prev) => {
            const updated = [...prev];
            const lastIdx = updated.length - 1;
            if (lastIdx >= 0 && updated[lastIdx].role === 'assistant') {
              const current = updated[lastIdx].content;
              updated[lastIdx] = {
                ...updated[lastIdx],
                content: current ? `${current}\n\n[Error: ${errMsg}]` : `⚠️ ${errMsg}`,
              };
            }
            return updated;
          });
          setLoading(false);
        }
      );
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
