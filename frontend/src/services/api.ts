import type {
  Conversation,
  ChatMessage,
  SystemHealth,
  SystemStatus,
  MCPServer,
  MemoryItem,
} from '../types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/system/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchSystemStatus(): Promise<SystemStatus> {
  const res = await fetch(`${API_BASE}/system/status`);
  if (!res.ok) throw new Error('Failed to fetch system status');
  return res.json();
}

export async function fetchConversations(): Promise<Conversation[]> {
  const res = await fetch(`${API_BASE}/conversations`);
  if (!res.ok) throw new Error('Failed to fetch conversations');
  const data = await res.json();
  return data.conversations;
}

export async function createConversation(title?: string): Promise<Conversation> {
  const res = await fetch(`${API_BASE}/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: title || 'New Conversation' }),
  });
  if (!res.ok) throw new Error('Failed to create conversation');
  return res.json();
}

export async function fetchConversationDetails(
  id: string
): Promise<{ conversation: Conversation; messages: ChatMessage[] }> {
  const res = await fetch(`${API_BASE}/conversations/${id}`);
  if (!res.ok) throw new Error('Failed to fetch conversation');
  return res.json();
}

export async function sendMessage(
  conversationId: string,
  content: string,
  role: 'user' | 'assistant' = 'user'
): Promise<ChatMessage> {
  const res = await fetch(`${API_BASE}/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role, content, metadata: {} }),
  });
  if (!res.ok) throw new Error('Failed to send message');
  return res.json();
}

export async function deleteConversation(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/conversations/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete conversation');
}

export async function fetchMCPServers(): Promise<MCPServer[]> {
  const res = await fetch(`${API_BASE}/mcp/servers`);
  if (!res.ok) throw new Error('Failed to fetch MCP servers');
  const data = await res.json();
  return data.servers;
}

export async function toggleMCPServer(id: string, enabled?: boolean): Promise<{ id: string; enabled: boolean }> {
  const res = await fetch(`${API_BASE}/mcp/servers/${id}/toggle`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enabled }),
  });
  if (!res.ok) throw new Error('Failed to toggle MCP server');
  return res.json();
}

export async function fetchMemories(): Promise<MemoryItem[]> {
  const res = await fetch(`${API_BASE}/memory`);
  if (!res.ok) throw new Error('Failed to fetch memories');
  const data = await res.json();
  return data.memories;
}

export async function fetchSettings(): Promise<any> {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
}

export async function fetchLLMStatus(): Promise<import('../types').LLMStatus> {
  const res = await fetch(`${API_BASE}/llm/status`);
  if (!res.ok) throw new Error('Failed to fetch LLM status');
  return res.json();
}

export async function testLLMConnection(provider: 'nvidia' | 'local'): Promise<any> {
  const res = await fetch(`${API_BASE}/llm/test-connection`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider }),
  });
  if (!res.ok) throw new Error('Failed to test connection');
  return res.json();
}

export async function selectProvider(
  provider: 'nvidia' | 'local',
  executionMode?: 'cloud' | 'local' | 'hybrid'
): Promise<any> {
  const res = await fetch(`${API_BASE}/llm/select-provider`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider, execution_mode: executionMode }),
  });
  if (!res.ok) throw new Error('Failed to update provider');
  return res.json();
}

export async function streamChat(
  conversationId: string,
  content: string,
  onToken: (token: string) => void,
  onComplete: () => void,
  onError: (error: string) => void,
  provider?: string
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conversation_id: conversationId,
        content,
        provider,
      }),
    });

    if (!response.ok) {
      throw new Error(`Chat stream failed: HTTP ${response.status}`);
    }

    if (!response.body) {
      throw new Error('Response body is null');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith('data: ')) continue;
        const dataStr = trimmed.slice(6);
        if (dataStr === '[DONE]') {
          onComplete();
          return;
        }
        try {
          const parsed = JSON.parse(dataStr);
          if (parsed.error) {
            onError(parsed.error);
          } else if (parsed.token) {
            onToken(parsed.token);
          }
        } catch {
          // Chunk parse error ignored
        }
      }
    }
    onComplete();
  } catch (err: any) {
    onError(err.message || 'Stream connection error');
  }
}

