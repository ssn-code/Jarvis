from typing import Literal, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config.settings import settings
from backend.llm.manager import llm_manager

router = APIRouter(prefix="/api/llm", tags=["LLM & Providers"])


class TestConnectionRequest(BaseModel):
    provider: Literal["nvidia", "local"] = "nvidia"


class SelectProviderRequest(BaseModel):
    provider: Literal["nvidia", "local"]
    execution_mode: Optional[Literal["cloud", "local", "hybrid"]] = None


@router.get("/status")
async def get_llm_status():
    """Retrieve health and configuration of all AI providers (API keys redacted)."""
    health_results = await llm_manager.health_check_all()

    return {
        "active_provider": settings.llm.provider,
        "execution_mode": settings.llm.execution_mode,
        "fallback_enabled": settings.llm.enable_fallback,
        "providers": {
            "nvidia": {
                "name": "NVIDIA API",
                "status": health_results["nvidia"].status,
                "model": settings.nvidia.model,
                "latency_ms": health_results["nvidia"].latency_ms,
                "configured": bool(settings.nvidia.api_key.get_secret_value()),
                "error": health_results["nvidia"].error,
            },
            "local": {
                "name": "Local LLM",
                "runtime": settings.local_llm.runtime,
                "status": health_results["local"].status,
                "model": settings.local_llm.model,
                "latency_ms": health_results["local"].latency_ms,
                "configured": True,
                "error": health_results["local"].error,
            },
        },
    }


@router.post("/test-connection")
async def test_provider_connection(req: TestConnectionRequest):
    """Test connection to a specified AI provider."""
    health = await llm_manager.health_check_provider(req.provider)
    return health


@router.post("/select-provider")
async def select_provider(req: SelectProviderRequest):
    """Change the active AI provider or execution mode at runtime."""
    settings.llm.provider = req.provider
    if req.execution_mode:
        settings.llm.execution_mode = req.execution_mode
    return {
        "status": "updated",
        "active_provider": settings.llm.provider,
        "execution_mode": settings.llm.execution_mode,
    }
