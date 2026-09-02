import React, { useState, useEffect } from 'react';
import { Sliders, Shield, Volume2, Bot, CheckCircle2 } from 'lucide-react';
import { fetchSettings } from '../services/api';

export const SettingsView: React.FC = () => {
  const [settingsData, setSettingsData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchSettings();
        setSettingsData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading || !settingsData) {
    return <div className="view-container"><p>Loading settings...</p></div>;
  }

  return (
    <div className="view-container">
      <div className="view-header">
        <div className="view-header-title">
          <Sliders size={22} className="accent-icon" />
          <h2>System Settings</h2>
        </div>
      </div>

      <div className="settings-sections">
        <div className="settings-card">
          <div className="settings-card-header">
            <Bot size={18} className="accent-icon" />
            <h3>AI Brain & Models</h3>
          </div>
          <div className="settings-row">
            <span>Planner Model:</span>
            <code>{settingsData.llm.planner_model}</code>
          </div>
          <div className="settings-row">
            <span>Chat Model:</span>
            <code>{settingsData.llm.chat_model}</code>
          </div>
          <div className="settings-row">
            <span>Coding Model:</span>
            <code>{settingsData.llm.coding_model}</code>
          </div>
          <div className="settings-row">
            <span>OpenRouter API Key:</span>
            <span className={settingsData.llm.has_api_key ? 'status-tag connected' : 'status-tag disconnected'}>
              {settingsData.llm.has_api_key ? 'Configured (Active)' : 'Not Set'}
            </span>
          </div>
        </div>

        <div className="settings-card">
          <div className="settings-card-header">
            <Volume2 size={18} className="accent-icon" />
            <h3>Voice System</h3>
          </div>
          <div className="settings-row">
            <span>Wake Word:</span>
            <code>{settingsData.voice.wake_word}</code>
          </div>
          <div className="settings-row">
            <span>Whisper Speech-to-Text:</span>
            <code>{settingsData.voice.whisper_model}</code>
          </div>
          <div className="settings-row">
            <span>Piper Voice:</span>
            <code>{settingsData.voice.piper_voice}</code>
          </div>
        </div>

        <div className="settings-card">
          <div className="settings-card-header">
            <Shield size={18} className="accent-icon" />
            <h3>Security & Sandbox</h3>
          </div>
          <div className="settings-row">
            <span>Default Verification:</span>
            <span className="permission-tag">{settingsData.security.default_verification_level}</span>
          </div>
          <div className="settings-row">
            <span>MCP Auto-Activation:</span>
            <span className="status-tag connected">
              <CheckCircle2 size={12} /> {settingsData.mcp.auto_activation ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
