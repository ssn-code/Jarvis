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
