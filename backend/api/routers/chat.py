import json
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.database.manager import db, utc_iso_now
from backend.core.models import MessageRole

router = APIRouter(prefix="/api", tags=["Chat & Conversations"])


class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Conversation"


class SendMessageRequest(BaseModel):
    role: MessageRole = MessageRole.USER
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.get("/conversations")
async def list_conversations():
    """Retrieve all conversations ordered by recent activity."""
    rows = await db.fetchall("SELECT * FROM conversations ORDER BY updated_at DESC")
    conversations = []
    for r in rows:
        try:
            meta = json.loads(r["metadata"]) if r["metadata"] else {}
        except Exception:
            meta = {}
        conversations.append({
            "id": r["id"],
            "title": r["title"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "metadata": meta,
        })
    return {"conversations": conversations}


@router.post("/conversations")
async def create_conversation(req: CreateConversationRequest):
    """Create a new conversation session."""
    conv_id = str(uuid.uuid4())
    now = utc_iso_now()
    title = req.title or "New Conversation"
    await db.execute(
        "INSERT INTO conversations (id, title, created_at, updated_at, metadata) VALUES (?, ?, ?, ?, ?)",
        (conv_id, title, now, now, "{}"),
    )
    return {
        "id": conv_id,
        "title": title,
        "created_at": now,
        "updated_at": now,
        "metadata": {},
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Retrieve conversation details and message history."""
    conv = await db.fetchone(
        "SELECT * FROM conversations WHERE id = ?",
        (conversation_id,)
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await db.fetchall(
        "SELECT * FROM messages WHERE conversation_id = ? ORDER BY id ASC",
        (conversation_id,)
    )
    formatted_msgs = []
    for m in messages:
        try:
            meta = json.loads(m["metadata"]) if m["metadata"] else {}
        except Exception:
            meta = {}
        try:
            tool_calls = json.loads(m["tool_calls"]) if m["tool_calls"] else None
        except Exception:
            tool_calls = None
        formatted_msgs.append({
            "id": m["id"],
            "conversation_id": m["conversation_id"],
            "role": m["role"],
            "content": m["content"],
            "tool_calls": tool_calls,
            "metadata": meta,
            "created_at": m["created_at"],
        })

    return {
        "conversation": dict(conv),
        "messages": formatted_msgs,
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation and all its messages."""
    await db.execute(
        "DELETE FROM conversations WHERE id = ?",
        (conversation_id,)
    )
    return {"status": "deleted", "id": conversation_id}


@router.post("/conversations/{conversation_id}/messages")
async def add_message(conversation_id: str, req: SendMessageRequest):
    """Add a message to a conversation."""
    conv = await db.fetchone(
        "SELECT * FROM conversations WHERE id = ?",
        (conversation_id,)
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    now = utc_iso_now()
    meta_json = json.dumps(req.metadata)
    msg_id = await db.execute(
        "INSERT INTO messages (conversation_id, role, content, metadata, created_at) VALUES (?, ?, ?, ?, ?)",
        (conversation_id, req.role.value, req.content, meta_json, now),
    )
    await db.execute(
        "UPDATE conversations SET updated_at = ? WHERE id = ?",
        (now, conversation_id),
    )
    return {
        "id": msg_id,
        "conversation_id": conversation_id,
        "role": req.role.value,
        "content": req.content,
        "created_at": now,
        "metadata": req.metadata,
    }
