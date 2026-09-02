import React, { useState, useEffect } from 'react';
import { Brain, Search, RefreshCw, Bookmark } from 'lucide-react';
import type { MemoryItem } from '../types';
import { fetchMemories } from '../services/api';

export const MemoryView: React.FC = () => {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const loadMemories = async () => {
    setLoading(true);
    try {
      const data = await fetchMemories();
      setMemories(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMemories();
  }, []);

  const filtered = memories.filter(
    (m) =>
      m.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.value.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="view-container">
      <div className="view-header">
        <div className="view-header-title">
          <Brain size={22} className="accent-icon" />
          <h2>Long-Term Memory</h2>
        </div>
        <button className="icon-btn-secondary" onClick={loadMemories} title="Refresh memory">
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      <p className="view-description">
        Selective persistent knowledge: preferences, project parameters, interaction rules, and important settings.
      </p>

      <div className="search-bar">
        <Search size={16} className="search-icon" />
        <input
          type="text"
          placeholder="Search stored memories..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      {filtered.length === 0 ? (
        <div className="empty-panel">
          <Brain size={36} className="empty-icon" />
          <p>No memories stored yet.</p>
          <span className="subtext">
            Memories are extracted during conversations and stored persistently in SQLite + ChromaDB.
          </span>
        </div>
      ) : (
        <div className="memory-cards-grid">
          {filtered.map((m) => (
            <div key={m.id || m.key} className="memory-card">
              <div className="memory-card-header">
                <div className="memory-key">
                  <Bookmark size={14} className="accent-icon" />
                  <strong>{m.key}</strong>
                </div>
                <span className="memory-category-tag">{m.category}</span>
              </div>
              <p className="memory-value">{m.value}</p>
              <div className="memory-footer">
                <span>Importance: {m.importance}/5</span>
                <span>{new Date(m.updated_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
