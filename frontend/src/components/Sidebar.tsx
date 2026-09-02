import React from 'react';
import {
  Plus,
  MessageSquare,
  Trash2,
  Server,
  Brain,
  Sliders,
  HardDrive,
  X,
} from 'lucide-react';
import type { Conversation, SystemStatus } from '../types';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string, e: React.MouseEvent) => void;
  systemStatus: SystemStatus | null;
  activeTab: 'chat' | 'mcp' | 'memory' | 'settings' | 'system';
  onSelectTab: (tab: 'chat' | 'mcp' | 'memory' | 'settings' | 'system') => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  systemStatus,
  activeTab,
  onSelectTab,
}) => {
  return (
    <>
      {isOpen && <div className="sidebar-backdrop" onClick={onClose} />}
      <aside className={`jarvis-sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={onNewConversation}>
            <Plus size={18} />
            <span>New conversation</span>
          </button>
          <button className="icon-btn close-btn" onClick={onClose} aria-label="Close sidebar">
            <X size={20} />
          </button>
        </div>

        <div className="conversations-section">
          <div className="section-label">Recent Conversations</div>
          <div className="conversations-list">
            {conversations.length === 0 ? (
              <div className="empty-state">No conversations yet</div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`conversation-item ${
                    activeTab === 'chat' && activeConversationId === conv.id ? 'active' : ''
                  }`}
                  onClick={() => {
                    onSelectConversation(conv.id);
                    onSelectTab('chat');
                  }}
                >
                  <MessageSquare size={16} className="conv-icon" />
                  <span className="conv-title">{conv.title}</span>
                  <button
                    className="delete-conv-btn"
                    onClick={(e) => onDeleteConversation(conv.id, e)}
                    title="Delete conversation"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="sidebar-footer">
          <button
            className={`footer-nav-item ${activeTab === 'mcp' ? 'active' : ''}`}
            onClick={() => onSelectTab('mcp')}
          >
            <Server size={18} />
            <span>MCP Servers</span>
          </button>
          <button
            className={`footer-nav-item ${activeTab === 'memory' ? 'active' : ''}`}
            onClick={() => onSelectTab('memory')}
          >
            <Brain size={18} />
            <span>Memory</span>
          </button>
          <button
            className={`footer-nav-item ${activeTab === 'system' ? 'active' : ''}`}
            onClick={() => onSelectTab('system')}
          >
            <HardDrive size={18} />
            <span>System Status</span>
          </button>
          <button
            className={`footer-nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => onSelectTab('settings')}
          >
            <Sliders size={18} />
            <span>Settings</span>
          </button>

          {systemStatus && (
            <div className="mini-telemetry">
              <span>CPU {Math.round(systemStatus.cpu_percent)}%</span>
              <span className="dot">•</span>
              <span>RAM {Math.round(systemStatus.memory_percent)}%</span>
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
