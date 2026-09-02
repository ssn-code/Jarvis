import React, { useRef, useEffect } from 'react';
import { Sparkles, User, Copy, Check } from 'lucide-react';
import type { ChatMessage } from '../types';

interface ChatAreaProps {
  messages: ChatMessage[];
  onSelectSuggestion: (prompt: string) => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({ messages, onSelectSuggestion }) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [copiedIndex, setCopiedIndex] = React.useState<number | null>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  if (messages.length === 0) {
    return (
      <div className="chat-empty-container">
        <div className="welcome-banner">
          <h1 className="welcome-title">
            <span>Hello,</span> <span className="gradient-text">I'm JARVIS.</span>
          </h1>
          <p className="welcome-subtitle">How can I help you today?</p>
        </div>

        <div className="suggestion-chips-grid">
          <button
            className="suggestion-chip"
            onClick={() => onSelectSuggestion("Check system health and resource metrics")}
          >
            <span className="chip-icon">📊</span>
            <div className="chip-content">
              <strong>System Status</strong>
              <span>Check host CPU, RAM, and disk metrics</span>
            </div>
          </button>

          <button
            className="suggestion-chip"
            onClick={() => onSelectSuggestion("List all registered MCP servers and tools")}
          >
            <span className="chip-icon">🔌</span>
            <div className="chip-content">
              <strong>MCP Servers</strong>
              <span>Explore tool registries & permissions</span>
            </div>
          </button>

          <button
            className="suggestion-chip"
            onClick={() => onSelectSuggestion("Remember my preferred coding stack and project defaults")}
          >
            <span className="chip-icon">🧠</span>
            <div className="chip-content">
              <strong>Long-Term Memory</strong>
              <span>Save preferences & personal context</span>
            </div>
          </button>

          <button
            className="suggestion-chip"
            onClick={() => onSelectSuggestion("Explain how JARVIS operates as an AI Assistant")}
          >
            <span className="chip-icon">⚡</span>
            <div className="chip-content">
              <strong>Architecture Overview</strong>
              <span>Learn about Gemini UI + MCP backend</span>
            </div>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-messages-container" ref={scrollRef}>
      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={`message-row ${msg.role === 'user' ? 'user-row' : 'assistant-row'}`}
        >
          <div className="message-avatar">
            {msg.role === 'user' ? (
              <User size={18} />
            ) : (
              <Sparkles size={18} className="sparkle-avatar" />
            )}
          </div>

          <div className="message-bubble-wrapper">
            <div className="message-bubble">
              <div className="message-text">{msg.content}</div>
            </div>

            <div className="message-meta">
              <span className="message-time">
                {new Date(msg.created_at).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
              <button
                className="copy-btn"
                onClick={() => handleCopy(msg.content, idx)}
                title="Copy message"
              >
                {copiedIndex === idx ? <Check size={13} /> : <Copy size={13} />}
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
