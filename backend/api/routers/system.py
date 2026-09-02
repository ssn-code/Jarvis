from fastapi import APIRouter
from backend.config.settings import settings
from backend.system.monitor import get_system_status
from backend.core.models import SystemStatus
from backend.database.manager import db

router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/health")
async def health_check():
    """Service health check endpoint."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "env": settings.env,
    }


@router.get("/status", response_model=SystemStatus)
async def system_status():
    """Returns real-time host resource metrics."""
    return get_system_status()


@router.get("/audit-logs")
async def get_audit_logs(limit: int = 50):
    """Retrieves recent audit logs from the database."""
    logs = await db.fetchall(
        "SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    return {"logs": logs}
