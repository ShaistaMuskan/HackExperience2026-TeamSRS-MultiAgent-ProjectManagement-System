"""
System/demo introspection endpoints - not part of the agentic pipeline itself.
Exists so a demo (or the dashboard) can show, live, which integrations are
currently backed by mock vs. real clients, without digging through logs.
"""
from __future__ import annotations
from fastapi import APIRouter

from app.core.config import get_integration_status, get_settings

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status", summary="Which integrations are mock vs. live right now")
async def integration_status():
    settings = get_settings()
    integrations = get_integration_status()
    live_count = sum(1 for v in integrations.values() if v["status"] == "live")
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "integrations": integrations,
        "summary": f"{live_count}/{len(integrations)} integrations live",
    }
