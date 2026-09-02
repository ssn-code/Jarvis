export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

export interface ChatMessage {
  id?: number;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  tool_calls?: any[] | null;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface SystemHealth {
  status: string;
  app: string;
  version: string;
  env: string;
}

export interface SystemStatus {
  cpu_percent: number;
  memory_used_mb: number;
  memory_total_mb: number;
  memory_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  disk_percent: number;
  os: string;
  uptime_seconds: number;
}

export interface MCPServer {
  id: string;
  name: string;
  description: string;
  command: string;
  args: string[];
  transport: string;
  status: string;
  enabled: boolean;
  auto_activation: boolean;
  permission_level: string;
}

export interface MemoryItem {
  id?: number;
  key: string;
  value: string;
  category: string;
  importance: number;
  created_at: string;
  updated_at: string;
}

export interface ProviderInfo {
  name: string;
  status: string;
  model: string;
  runtime?: string;
  latency_ms?: number | null;
  configured: boolean;
  error?: string | null;
}

export interface LLMStatus {
  active_provider: string;
  execution_mode: 'cloud' | 'local' | 'hybrid';
  fallback_enabled: boolean;
  providers: {
    nvidia: ProviderInfo;
    local: ProviderInfo;
  };
}
