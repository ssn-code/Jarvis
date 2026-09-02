from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from backend.database.manager import db, utc_iso_now
from backend.core.models import MemoryCategory

router = APIRouter(prefix="/api/memory", tags=["Memory"])


class MemoryCreateRequest(BaseModel):
    key: str
    value: str
    category: MemoryCategory = MemoryCategory.PREFERENCE
    importance: int = Field(default=1, ge=1, le=5)


@router.get("")
async def list_memories(category: Optional[str] = None):
    """Retrieve all persistent memories, optionally filtered by category."""
    if category:
        rows = await db.fetchall(
            "SELECT * FROM memories WHERE category = ? ORDER BY importance DESC, updated_at DESC",
            (category,)
        )
    else:
        rows = await db.fetchall("SELECT * FROM memories ORDER BY importance DESC, updated_at DESC")
    return {"memories": rows}


@router.post("")
async def create_or_update_memory(req: MemoryCreateRequest):
    """Create or update a memory item."""
    now = utc_iso_now()
    existing = await db.fetchone("SELECT id FROM memories WHERE key = ?", (req.key,))
    if existing:
        await db.execute(
            "UPDATE memories SET value = ?, category = ?, importance = ?, updated_at = ? WHERE key = ?",
            (req.value, req.category.value, req.importance, now, req.key),
        )
        return {"status": "updated", "key": req.key}
    else:
        mem_id = await db.execute(
            "INSERT INTO memories (key, value, category, importance, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (req.key, req.value, req.category.value, req.importance, now, now),
        )
        return {"status": "created", "id": mem_id, "key": req.key}


@router.delete("/{memory_id}")
async def delete_memory(memory_id: int):
    """Delete a memory entry by ID."""
    await db.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    return {"status": "deleted", "id": memory_id}


@router.get("/search")
async def search_memories(q: str = Query(..., description="Query string to search memory keys and values")):
    """Search memories by keyword match."""
    like_query = f"%{q}%"
    rows = await db.fetchall(
        "SELECT * FROM memories WHERE key LIKE ? OR value LIKE ? ORDER BY importance DESC",
        (like_query, like_query),
    )
    return {"query": q, "results": rows}
