import React, { useState, useEffect } from 'react';
import { Cpu, HardDrive, RefreshCw, Activity, Clock, Monitor } from 'lucide-react';
import type { SystemStatus } from '../types';
import { fetchSystemStatus } from '../services/api';

export const SystemView: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const data = await fetchSystemStatus();
      setStatus(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="view-container">
      <div className="view-header">
        <div className="view-header-title">
          <Activity size={22} className="accent-icon" />
          <h2>Host System Status</h2>
        </div>
        <button className="icon-btn-secondary" onClick={loadStatus} title="Refresh metrics">
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      <p className="view-description">
        Real-time telemetry and resource usage monitored safely with zero-overhead async probes.
      </p>

      {status && (
        <div className="telemetry-grid">
          <div className="telemetry-card">
            <div className="telemetry-header">
              <Cpu size={20} className="telemetry-icon" />
              <span>CPU Utilization</span>
            </div>
            <div className="telemetry-value">{status.cpu_percent}%</div>
            <div className="meter-bar">
              <div
                className="meter-fill"
                style={{
                  width: `${Math.min(status.cpu_percent, 100)}%`,
                  backgroundColor: status.cpu_percent > 80 ? 'var(--accent-coral)' : 'var(--accent-blue)',
                }}
              />
            </div>
          </div>

          <div className="telemetry-card">
            <div className="telemetry-header">
              <Activity size={20} className="telemetry-icon" />
              <span>RAM Memory</span>
            </div>
            <div className="telemetry-value">
              {status.memory_percent}%
              <span className="telemetry-subval">
                ({(status.memory_used_mb / 1024).toFixed(1)} GB / {(status.memory_total_mb / 1024).toFixed(1)} GB)
              </span>
            </div>
            <div className="meter-bar">
              <div
                className="meter-fill"
                style={{
                  width: `${status.memory_percent}%`,
                  backgroundColor: status.memory_percent > 85 ? 'var(--accent-coral)' : 'var(--accent-purple)',
                }}
              />
            </div>
          </div>

          <div className="telemetry-card">
            <div className="telemetry-header">
              <HardDrive size={20} className="telemetry-icon" />
              <span>Disk Storage</span>
            </div>
            <div className="telemetry-value">
              {status.disk_percent}%
              <span className="telemetry-subval">
                ({status.disk_used_gb} GB / {status.disk_total_gb} GB)
              </span>
            </div>
            <div className="meter-bar">
              <div
                className="meter-fill"
                style={{
                  width: `${status.disk_percent}%`,
                  backgroundColor: status.disk_percent > 90 ? 'var(--accent-coral)' : 'var(--accent-green)',
                }}
              />
            </div>
          </div>

          <div className="telemetry-card">
            <div className="telemetry-header">
              <Monitor size={20} className="telemetry-icon" />
              <span>Environment & OS</span>
            </div>
            <div className="telemetry-info-text">{status.os}</div>
            <div className="telemetry-uptime">
              <Clock size={14} />
              <span>Uptime: {Math.floor(status.uptime_seconds)}s</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
