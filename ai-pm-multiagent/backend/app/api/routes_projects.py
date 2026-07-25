"""Project lifecycle endpoints: ingest brief -> Atlas plans & executes -> query results."""
from __future__ import annotations
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import IngestBriefRequest
from app.core.config import get_blob_client, get_settings
from app.core.security import get_current_user, require_permission, CurrentUser
from app.core.logging import get_logger
from app.db import get_repository
from app.agents import get_atlas
from app.models import ProjectBrief, TaskStatus

router = APIRouter(prefix="/projects", tags=["projects"])
logger = get_logger("api.projects")


@router.post("/ingest", summary="Upload a project brief and let Atlas plan + execute the project")
async def ingest_project(req: IngestBriefRequest, user: CurrentUser = Depends(get_current_user)):
    require_permission(user, "write")
    brief = ProjectBrief(
        source_filename=req.source_filename, source_type=req.source_type,
        raw_text=req.raw_text, uploaded_by=req.uploaded_by,
    )

    # Archive the raw brief in Blob Storage before Atlas processes it - mirrors
    # the architecture diagram's Project Brief -> Azure Blob Storage -> RAG flow.
    # Non-fatal: ingestion still proceeds even if archival fails, so a Blob
    # Storage outage/misconfiguration never blocks Atlas from planning.
    try:
        blob_client = get_blob_client()
        settings = get_settings()
        blob_name = f"{brief.id}_{brief.source_filename}"
        brief.blob_url = await blob_client.upload_file(
            container=settings.azure_storage_container_briefs,
            blob_name=blob_name,
            content_bytes=brief.raw_text.encode("utf-8"),
        )
    except Exception as exc:
        logger.warning(f"Brief archival to Blob Storage failed (continuing anyway): {exc}")

    atlas = get_atlas()
    project = await atlas.run_full_pipeline(brief, project_name=req.project_name)
    return project


@router.get("/")
async def list_projects(user: CurrentUser = Depends(get_current_user)):
    return get_repository().list_projects()


@router.get("/{project_id}")
async def get_project(project_id: str, user: CurrentUser = Depends(get_current_user)):
    project = get_repository().get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.get("/{project_id}/tasks")
async def get_tasks(project_id: str, user: CurrentUser = Depends(get_current_user)):
    return get_repository().list_tasks(project_id)


@router.get("/{project_id}/milestones")
async def get_milestones(project_id: str, user: CurrentUser = Depends(get_current_user)):
    return get_repository().list_milestones(project_id)


@router.get("/{project_id}/sprints")
async def get_sprints(project_id: str, user: CurrentUser = Depends(get_current_user)):
    return get_repository().list_sprints(project_id)


@router.get("/{project_id}/dependencies")
async def get_dependencies(project_id: str, user: CurrentUser = Depends(get_current_user)):
    return get_repository().list_dependencies(project_id)


@router.get("/{project_id}/risks")
async def get_risks(project_id: str, user: CurrentUser = Depends(get_current_user)):
    return get_repository().list_risks(project_id)


@router.get("/{project_id}/notifications")
async def get_notifications(project_id: str, user: CurrentUser = Depends(get_current_user)):
    return get_repository().list_notifications(project_id)


@router.post(
    "/{project_id}/demo/simulate-issues",
    summary="[Demo helper] Backdate a task and free up a resource so Sentinel finds a risk on the next pass",
)
async def simulate_issues(project_id: str, user: CurrentUser = Depends(get_current_user)):
    """
    Not part of the agentic pipeline - this exists purely so a live demo doesn't
    have to wait for real calendar time to pass before Sentinel has something to
    detect. It backdates one in-flight task's due date (-> overdue) and marks one
    resource unavailable, both of which risk_tools.py's detectors pick up on the
    next Sentinel pass (POST /agents/sentinel/monitor/{project_id}).
    """
    require_permission(user, "write")
    repo = get_repository()
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    tasks = repo.list_tasks(project_id)
    if not tasks:
        raise HTTPException(400, "Project has no tasks yet - ingest a brief first")

    target = next((t for t in tasks if t.status != TaskStatus.COMPLETED), tasks[0])
    target.status = TaskStatus.IN_PROGRESS
    # >5 days late crosses risk_tools.py's CRITICAL severity threshold, which is
    # what makes the Orchestrator auto-route this to the Human Approval Agent.
    target.due_date = datetime.utcnow() - timedelta(days=6)

    resources = repo.list_resources()
    affected = resources[0] if resources else None
    if affected:
        # Assign the overdue task TO the resource we're about to mark
        # unavailable, so the two aren't independent facts - this is what lets
        # risk_tools.find_reassignment_candidate() identify a single concrete
        # {task, replacement resource} pairing, which is what makes the
        # Orchestrator route the resulting critical risk to an auto-executing
        # REASSIGN_RESOURCE approval instead of a generic escalation.
        target.assignee = affected.email
        affected.is_available = False
    repo.save_task(target)

    return {
        "message": "Simulated a schedule slip and a resource outage on the same task. "
                   f"Now call POST /agents/sentinel/monitor/{project_id} to see Sentinel detect it "
                   "and auto-route a reassignment approval.",
        "overdue_task": {"id": target.id, "title": target.title, "due_date": target.due_date, "assignee": target.assignee},
        "unavailable_resource": {"id": affected.id, "name": affected.name} if affected else None,
    }
