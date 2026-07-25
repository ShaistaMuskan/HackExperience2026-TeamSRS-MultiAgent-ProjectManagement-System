"""Aggregated dashboard + executive status report endpoints for the frontend."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user, CurrentUser
from app.db import get_repository
from app.tools import risk_tools, status_tools

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{project_id}")
async def get_dashboard(project_id: str, user: CurrentUser = Depends(get_current_user)):
    repo = get_repository()
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    tasks = repo.list_tasks(project_id)
    milestones = repo.list_milestones(project_id)
    risks = repo.list_risks(project_id)
    sprints = repo.list_sprints(project_id)
    dependencies = repo.list_dependencies(project_id)
    resources = repo.list_resources()
    approvals = repo.list_approvals(project_id)
    notifications = repo.list_notifications(project_id)

    health = risk_tools.calculate_project_risk(project, tasks, risks, resources)

    return {
        "project": project,
        "health": health,
        "tasks": tasks,
        "milestones": milestones,
        "risks": risks,
        "sprints": sprints,
        "dependencies": dependencies,
        "approvals": approvals,
        "notifications": notifications[-20:],
        "task_summary": {
            "total": len(tasks),
            "completed": sum(1 for t in tasks if t.status == "completed"),
            "in_progress": sum(1 for t in tasks if t.status == "in_progress"),
            "overdue": health.tasks_overdue,
            "not_started": sum(1 for t in tasks if t.status == "not_started"),
        },
    }


@router.get("/{project_id}/status-report")
async def get_status_report(project_id: str, user: CurrentUser = Depends(get_current_user)):
    repo = get_repository()
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    tasks = repo.list_tasks(project_id)
    risks = repo.list_risks(project_id)
    resources = repo.list_resources()
    health = risk_tools.calculate_project_risk(project, tasks, risks, resources)
    report = await status_tools.generate_status_report(project, tasks, risks, health)
    return {"report": report, "health": health}
