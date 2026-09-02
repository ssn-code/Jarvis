import React, { useState, useEffect } from 'react';
import {
  Sliders,
  Shield,
  Volume2,
  Bot,
  CheckCircle2,
  Cpu,
  RefreshCw,
  Zap,
  Check,
  AlertCircle,
  ToggleRight,
  ToggleLeft,
} from 'lucide-react';
import { fetchSettings, fetchLLMStatus, testLLMConnection, selectProvider } from '../services/api';
import type { LLMStatus } from '../types';

export const SettingsView: React.FC = () => {
  const [settingsData, setSettingsData] = useState<any>(null);
  const [llmStatus, setLlmStatus] = useState<LLMStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [testingNvidia, setTestingNvidia] = useState(false);
  const [testingLocal, setTestingLocal] = useState(false);
  const [testResultNvidia, setTestResultNvidia] = useState<string | null>(null);
  const [testResultLocal, setTestResultLocal] = useState<string | null>(null);
  const [fallbackEnabled, setFallbackEnabled] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [s, l] = await Promise.all([fetchSettings(), fetchLLMStatus()]);
      setSettingsData(s);
      setLlmStatus(l);
      setFallbackEnabled(l.fallback_enabled);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleModeChange = async (mode: 'cloud' | 'local' | 'hybrid') => {
    try {
      const provider = mode === 'local' ? 'local' : 'nvidia';
      await selectProvider(provider, mode);
      setLlmStatus((prev) => (prev ? { ...prev, execution_mode: mode, active_provider: provider } : null));
    } catch (err) {
      console.error('Failed to change execution mode', err);
    }
  };

  const handleTestNvidia = async () => {
    setTestingNvidia(true);
    setTestResultNvidia(null);
    try {
      const res = await testLLMConnection('nvidia');
      if (res.status === 'connected') {
        setTestResultNvidia(`Connected (${res.latency_ms}ms)`);
      } else {
        setTestResultNvidia(res.error || res.status);
      }
    } catch (err: any) {
      setTestResultNvidia(`Error: ${err.message}`);
    } finally {
      setTestingNvidia(false);
    }
  };

  const handleTestLocal = async () => {
    setTestingLocal(true);
    setTestResultLocal(null);
    try {
      const res = await testLLMConnection('local');
      if (res.status === 'connected') {
        setTestResultLocal(`Available (${res.latency_ms}ms)`);
      } else {
        setTestResultLocal(res.error || res.status);
      }
    } catch (err: any) {
      setTestResultLocal(`Error: ${err.message}`);
    } finally {
      setTestingLocal(false);
    }
  };

  if (loading || !settingsData || !llmStatus) {
    return <div className="view-container"><p>Loading settings...</p></div>;
  }

  return (
    <div className="view-container">
      <div className="view-header">
        <div className="view-header-title">
          <Sliders size={22} className="accent-icon" />
          <h2>AI Models & Settings</h2>
        </div>
        <button className="icon-btn-secondary" onClick={loadData} title="Refresh settings">
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="settings-sections">
        {/* Execution Mode */}
        <div className="settings-card">
          <div className="settings-card-header">
            <Zap size={18} className="accent-icon" />
            <h3>Execution Mode</h3>
          </div>
          <div className="mode-selector-row">
            {(['cloud', 'local', 'hybrid'] as const).map((m) => (
              <button
                key={m}
                className={`mode-pill ${llmStatus.execution_mode === m ? 'active' : ''}`}
                onClick={() => handleModeChange(m)}
              >
                <span className="radio-dot" />
                <span className="mode-name">{m.charAt(0).toUpperCase() + m.slice(1)}</span>
                <span className="mode-desc">
                  {m === 'cloud' && '(Primary NVIDIA API)'}
                  {m === 'local' && '(Local Ollama / 7B-8B)'}
                  {m === 'hybrid' && '(Simple Local + Complex NVIDIA)'}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* NVIDIA API Card */}
        <div className="settings-card">
          <div className="settings-card-header">
            <Bot size={18} className="accent-icon" />
            <h3>NVIDIA API (Primary Cloud AI)</h3>
          </div>
          <div className="settings-row">
            <span>Status:</span>
            <span
              className={`status-tag ${
                llmStatus.providers.nvidia.status === 'connected' ? 'connected' : 'disconnected'
              }`}
            >
              <CheckCircle2 size={12} />
              {llmStatus.providers.nvidia.status === 'connected'
                ? 'Connected'
                : llmStatus.providers.nvidia.status === 'not_configured'
                ? 'Not Configured (Set NVIDIA_API_KEY)'
                : 'Unavailable'}
            </span>
          </div>
          <div className="settings-row">
            <span>Configured Model:</span>
            <code>{llmStatus.providers.nvidia.model}</code>
          </div>
          <div className="settings-action-row">
            <button
              className="test-btn"
              onClick={handleTestNvidia}
              disabled={testingNvidia}
            >
              {testingNvidia ? 'Testing...' : 'Test Connection'}
            </button>
            {testResultNvidia && (
              <span className="test-result-pill">
                {testResultNvidia.includes('Connected') ? (
                  <Check size={12} className="accent-green" />
                ) : (
                  <AlertCircle size={12} className="accent-coral" />
                )}
                {testResultNvidia}
              </span>
            )}
          </div>
        </div>

        {/* Local Model Card */}
        <div className="settings-card">
          <div className="settings-card-header">
            <Cpu size={18} className="accent-icon" />
            <h3>Local Model (RTX 4050 6GB / Quantized)</h3>
          </div>
          <div className="settings-row">
            <span>Runtime:</span>
            <code>{llmStatus.providers.local.runtime || 'Ollama'}</code>
          </div>
          <div className="settings-row">
            <span>Model:</span>
            <code>{llmStatus.providers.local.model}</code>
          </div>
          <div className="settings-row">
            <span>Status:</span>
            <span
              className={`status-tag ${
                llmStatus.providers.local.status === 'connected' ? 'connected' : 'disconnected'
              }`}
            >
              <CheckCircle2 size={12} />
              {llmStatus.providers.local.status === 'connected' ? 'Available' : 'Offline'}
            </span>
          </div>
          <div className="settings-action-row">
            <button
              className="test-btn"
              onClick={handleTestLocal}
              disabled={testingLocal}
            >
              {testingLocal ? 'Testing...' : 'Test Connection'}
            </button>
            {testResultLocal && (
              <span className="test-result-pill">
                {testResultLocal.includes('Available') ? (
                  <Check size={12} className="accent-green" />
                ) : (
                  <AlertCircle size={12} className="accent-coral" />
                )}
                {testResultLocal}
              </span>
            )}
          </div>
        </div>

        {/* Fallback System */}
        <div className="settings-card">
          <div className="settings-card-header">
            <Shield size={18} className="accent-icon" />
            <h3>Model Fallback</h3>
          </div>
          <div className="settings-row">
            <div>
              <strong>Automatic Model Fallback</strong>
              <p className="subtext">
                Switch seamlessly to the secondary model if the primary cloud model encounters an outage.
              </p>
            </div>
            <button
              className="toggle-btn"
              onClick={() => setFallbackEnabled(!fallbackEnabled)}
            >
              {fallbackEnabled ? (
                <ToggleRight size={32} className="toggle-active" />
              ) : (
                <ToggleLeft size={32} className="toggle-inactive" />
              )}
            </button>
          </div>
        </div>

        {/* Voice System */}
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
            <span>Piper TTS Voice:</span>
            <code>{settingsData.voice.piper_voice}</code>
          </div>
        </div>
      </div>
    </div>
  );
};
