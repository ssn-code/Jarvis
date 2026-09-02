from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class PermissionLevel(str, Enum):
    READ_ONLY = "READ_ONLY"
    AUTOMATIC = "AUTOMATIC"
    USER_APPROVAL = "USER_APPROVAL"
    RESTRICTED = "RESTRICTED"
    BLOCKED = "BLOCKED"


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    DANGEROUS = "DANGEROUS"
    BLOCKED = "BLOCKED"


class ChatMessage(BaseModel):
    id: Optional[int] = None
    conversation_id: str
    role: MessageRole
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class Conversation(BaseModel):
    id: str
    title: str = "New Conversation"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryCategory(str, Enum):
    PREFERENCE = "preference"
    PROJECT = "project"
    FACT = "fact"
    SYSTEM = "system"
    INSTRUCTION = "instruction"


class MemoryItem(BaseModel):
    id: Optional[int] = None
    key: str
    value: str
    category: MemoryCategory = MemoryCategory.PREFERENCE
    importance: int = Field(default=1, ge=1, le=5)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class MCPServerStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class MCPServerRecord(BaseModel):
    id: str
    name: str
    description: str = ""
    command: str = ""
    args: List[str] = Field(default_factory=list)
    transport: str = "stdio"
    status: MCPServerStatus = MCPServerStatus.DISCONNECTED
    enabled: bool = True
    auto_activation: bool = True
    permission_level: PermissionLevel = PermissionLevel.AUTOMATIC


class MCPToolRecord(BaseModel):
    id: str
    server_id: str
    name: str
    description: str = ""
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.SAFE


class ToolExecutionRecord(BaseModel):
    id: Optional[int] = None
    tool_name: str
    server_id: Optional[str] = None
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[str] = None
    status: str = "success"
    execution_time_ms: float = 0.0
    created_at: datetime = Field(default_factory=utc_now)


class AuditLogEntry(BaseModel):
    id: Optional[int] = None
    timestamp: datetime = Field(default_factory=utc_now)
    user: str = "user"
    mcp_server: Optional[str] = None
    tool: Optional[str] = None
    arguments: Optional[str] = None
    permission: str = "AUTOMATIC"
    approval: str = "APPROVED"
    result: Optional[str] = None
    execution_time_ms: float = 0.0
    error: Optional[str] = None


class SystemStatus(BaseModel):
    cpu_percent: float
    memory_used_mb: float
    memory_total_mb: float
    memory_percent: float
    disk_used_gb: float
    disk_total_gb: float
    disk_percent: float
    os: str
    uptime_seconds: float
