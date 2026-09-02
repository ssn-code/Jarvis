import React, { useState, useEffect } from 'react';
import { Server, ToggleLeft, ToggleRight, RefreshCw, CheckCircle2, ShieldAlert } from 'lucide-react';
import type { MCPServer } from '../types';
import { fetchMCPServers, toggleMCPServer } from '../services/api';

export const MCPView: React.FC = () => {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(true);

  const loadServers = async () => {
    setLoading(true);
    try {
      const data = await fetchMCPServers();
      setServers(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadServers();
  }, []);

  const handleToggle = async (id: string, current: boolean) => {
    try {
      await toggleMCPServer(id, !current);
      setServers((prev) =>
        prev.map((s) => (s.id === id ? { ...s, enabled: !current } : s))
      );
    } catch (err) {
      console.error('Failed to toggle MCP server', err);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div className="view-header-title">
          <Server size={22} className="accent-icon" />
          <h2>MCP Servers Registry</h2>
        </div>
        <button className="icon-btn-secondary" onClick={loadServers} title="Refresh servers">
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      <p className="view-description">
        Model Context Protocol (MCP) provides standardized integration for external tools,
        filesystems, browsers, and operating system capabilities.
      </p>

      {servers.length === 0 ? (
        <div className="empty-panel">
          <Server size={36} className="empty-icon" />
          <p>No MCP servers registered yet.</p>
          <span className="subtext">
            Standard servers (Filesystem, Browser, Git) can be configured in Phase J5.
          </span>
        </div>
      ) : (
        <div className="mcp-server-cards">
          {servers.map((s) => (
            <div key={s.id} className="mcp-card">
              <div className="mcp-card-header">
                <div>
                  <h3 className="mcp-server-name">{s.name}</h3>
                  <span className="mcp-transport-badge">{s.transport}</span>
                </div>
                <button
                  className="toggle-btn"
                  onClick={() => handleToggle(s.id, s.enabled)}
                  title={s.enabled ? 'Disable server' : 'Enable server'}
                >
                  {s.enabled ? (
                    <ToggleRight size={32} className="toggle-active" />
                  ) : (
                    <ToggleLeft size={32} className="toggle-inactive" />
                  )}
                </button>
              </div>

              <p className="mcp-description">{s.description || 'No description provided.'}</p>

              <div className="mcp-meta-row">
                <div className="mcp-meta-item">
                  <span className="label">Status:</span>
                  <span className={`status-tag ${s.status}`}>
                    <CheckCircle2 size={12} /> {s.status}
                  </span>
                </div>
                <div className="mcp-meta-item">
                  <span className="label">Permission:</span>
                  <span className="permission-tag">
                    <ShieldAlert size={12} /> {s.permission_level}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
