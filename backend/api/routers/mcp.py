import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.database.manager import db
from backend.core.models import PermissionLevel, RiskLevel

router = APIRouter(prefix="/api/mcp", tags=["MCP"])


class RegisterServerRequest(BaseModel):
    id: str
    name: str
    description: str = ""
    command: str = ""
    args: List[str] = Field(default_factory=list)
    transport: str = "stdio"
    enabled: bool = True
    auto_activation: bool = True
    permission_level: PermissionLevel = PermissionLevel.AUTOMATIC


class ToggleServerRequest(BaseModel):
    enabled: Optional[bool] = None


@router.get("/servers")
async def list_mcp_servers():
    """List all registered MCP servers with their status and configuration."""
    rows = await db.fetchall("SELECT * FROM mcp_servers ORDER BY name ASC")
    servers = []
    for r in rows:
        try:
            args = json.loads(r["args"]) if r["args"] else []
        except Exception:
            args = []
        servers.append({
            "id": r["id"],
            "name": r["name"],
            "description": r["description"],
            "command": r["command"],
            "args": args,
            "transport": r["transport"],
            "status": r["status"],
            "enabled": bool(r["enabled"]),
            "auto_activation": bool(r["auto_activation"]),
            "permission_level": r["permission_level"],
        })
    return {"servers": servers}


@router.post("/servers")
async def register_mcp_server(req: RegisterServerRequest):
    """Register a new MCP server in the registry."""
    args_json = json.dumps(req.args)
    existing = await db.fetchone("SELECT id FROM mcp_servers WHERE id = ?", (req.id,))
    if existing:
        await db.execute(
            """UPDATE mcp_servers SET name = ?, description = ?, command = ?, args = ?,
               transport = ?, enabled = ?, auto_activation = ?, permission_level = ?
               WHERE id = ?""",
            (req.name, req.description, req.command, args_json, req.transport,
             1 if req.enabled else 0, 1 if req.auto_activation else 0,
             req.permission_level.value, req.id),
        )
        return {"status": "updated", "id": req.id}
    else:
        await db.execute(
            """INSERT INTO mcp_servers (id, name, description, command, args, transport, enabled, auto_activation, permission_level)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (req.id, req.name, req.description, req.command, args_json, req.transport,
             1 if req.enabled else 0, 1 if req.auto_activation else 0,
             req.permission_level.value),
        )
        return {"status": "registered", "id": req.id}


@router.post("/servers/{server_id}/toggle")
async def toggle_mcp_server(server_id: str, req: ToggleServerRequest):
    """Toggle an MCP server's enabled state."""
    server = await db.fetchone("SELECT * FROM mcp_servers WHERE id = ?", (server_id,))
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")

    new_state = req.enabled if req.enabled is not None else not bool(server["enabled"])
    await db.execute(
        "UPDATE mcp_servers SET enabled = ? WHERE id = ?",
        (1 if new_state else 0, server_id),
    )
    return {"id": server_id, "enabled": new_state}


@router.get("/tools")
async def list_mcp_tools(server_id: Optional[str] = None):
    """List discovered MCP tools, optionally filtered by server."""
    if server_id:
        rows = await db.fetchall("SELECT * FROM mcp_tools WHERE server_id = ?", (server_id,))
    else:
        rows = await db.fetchall("SELECT * FROM mcp_tools")
    tools = []
    for r in rows:
        try:
            in_schema = json.loads(r["input_schema"]) if r["input_schema"] else {}
        except Exception:
            in_schema = {}
        try:
            out_schema = json.loads(r["output_schema"]) if r["output_schema"] else {}
        except Exception:
            out_schema = {}
        tools.append({
            "id": r["id"],
            "server_id": r["server_id"],
            "name": r["name"],
            "description": r["description"],
            "input_schema": in_schema,
            "output_schema": out_schema,
            "risk_level": r["risk_level"],
        })
    return {"tools": tools}
