import React from 'react';
import { Menu, Sparkles, Activity } from 'lucide-react';
import type { SystemHealth } from '../types';

interface HeaderProps {
  onToggleSidebar: () => void;
  health: SystemHealth | null;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar, health }) => {
  return (
    <header className="jarvis-header">
      <div className="header-left">
        <button
          className="icon-btn"
          onClick={onToggleSidebar}
          aria-label="Toggle navigation drawer"
          title="Menu"
        >
          <Menu size={22} />
        </button>
        <div className="brand-container">
          <div className="sparkle-icon-wrapper">
            <Sparkles size={20} className="sparkle-icon" />
          </div>
          <span className="brand-title">JARVIS</span>
          <span className="brand-version">v{health?.version || '0.1.0'}</span>
        </div>
      </div>

      <div className="header-right">
        <div className="system-pill" title={health ? `Connected to ${health.env}` : 'Connecting...'}>
          <Activity size={14} className={health ? 'pulse-green' : 'pulse-amber'} />
          <span className="pill-text">{health ? 'Online' : 'Offline'}</span>
        </div>
      </div>
    </header>
  );
};
