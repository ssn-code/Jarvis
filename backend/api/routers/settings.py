from typing import Any, Dict
from fastapi import APIRouter
from pydantic import BaseModel
from backend.config.settings import settings
from backend.database.manager import db, utc_iso_now

router = APIRouter(prefix="/api/settings", tags=["Settings"])


class UpdateSettingRequest(BaseModel):
    key: str
    value: str


@router.get("")
async def get_settings():
    """Retrieve system configuration settings (with secrets redacted)."""
    db_settings_rows = await db.fetchall("SELECT key, value FROM settings")
    overrides = {r["key"]: r["value"] for r in db_settings_rows}

    return {
        "env": settings.env,
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "llm": {
            "api_url": settings.openrouter.api_url,
            "has_api_key": bool(settings.openrouter.api_key.get_secret_value()),
            "planner_model": settings.openrouter.planner_model,
            "chat_model": settings.openrouter.chat_model,
            "coding_model": settings.openrouter.coding_model,
            "vision_model": settings.openrouter.vision_model,
            "local_model": settings.local_llm.model,
        },
        "voice": {
            "wake_word": settings.voice.wake_word,
            "whisper_model": settings.voice.whisper_model,
            "piper_voice": settings.voice.piper_voice,
            "continuous_listening": settings.voice.continuous_listening,
            "push_to_talk": settings.voice.push_to_talk,
        },
        "security": {
            "default_verification_level": settings.security.default_verification_level,
            "has_encryption_key": bool(settings.security.encryption_key.get_secret_value()),
        },
        "presentation": {
            "theme": settings.presentation.theme,
            "api_host": settings.presentation.api_host,
            "api_port": settings.presentation.api_port,
        },
        "mcp": {
            "auto_activation": settings.mcp.auto_activation,
            "connect_timeout_seconds": settings.mcp.connect_timeout_seconds,
        },
        "custom_overrides": overrides,
    }


@router.post("")
async def update_custom_setting(req: UpdateSettingRequest):
    """Store or update a custom user setting in the database."""
    now = utc_iso_now()
    existing = await db.fetchone("SELECT key FROM settings WHERE key = ?", (req.key,))
    if existing:
        await db.execute(
            "UPDATE settings SET value = ?, updated_at = ? WHERE key = ?",
            (req.value, now, req.key),
        )
    else:
        await db.execute(
            "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            (req.key, req.value, now),
        )
    return {"status": "saved", "key": req.key, "value": req.value}
