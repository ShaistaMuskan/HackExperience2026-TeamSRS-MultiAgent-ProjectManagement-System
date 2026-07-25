"""Agent introspection + on-demand trigger endpoints (memory, manual Sentinel pass, orchestrator state)."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user, CurrentUser
from app.memory import get_memory_store
from app.orchestration import get_event_bus
from app.agents import get_sentinel, get_orchestrator

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/sentinel/monitor/{project_id}", summary="Manually trigger one Sentinel monitoring pass")
async def trigger_sentinel(project_id: str, user: CurrentUser = Depends(get_current_user)):
    sentinel = get_sentinel()
    try:
        result = await sentinel.monitor_project(project_id)
    except KeyError as e:
        raise HTTPException(404, str(e))
    return {
        "health": result["health"],
        "new_risks": result["new_risks"],
        "mitigations": result["mitigations"],
    }


@router.get("/memory/{agent_id}/{project_id}")
async def get_agent_memory(agent_id: str, project_id: str, user: CurrentUser = Depends(get_current_user)):
    return get_memory_store().get_or_create(agent_id, project_id)


@router.get("/orchestrator/state/{project_id}")
async def get_orchestrator_state(project_id: str, user: CurrentUser = Depends(get_current_user)):
    return get_orchestrator().get_state(project_id)


@router.get("/events/{project_id}", summary="Full event history for a project (audit trail)")
async def get_event_history(project_id: str, user: CurrentUser = Depends(get_current_user)):
    return get_event_bus().history(project_id)
