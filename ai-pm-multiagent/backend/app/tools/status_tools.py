"""Tool: project status updates and executive report generation."""
from __future__ import annotations
from datetime import datetime

from app.core.config import get_llm_client
from app.core.logging import get_logger
from app.models import Project, ProjectHealth, Risk, Task, HealthStatus

logger = get_logger("tools.status")


async def update_project_status(project: Project, health: ProjectHealth) -> Project:
    project.health = health.status
    project.updated_at = datetime.utcnow()
    logger.info(f"Project {project.id} status -> {health.status} ({health.summary})")
    return project


async def generate_status_report(project: Project, tasks: list[Task], risks: list[Risk], health: ProjectHealth) -> str:
    llm = get_llm_client()
    context = (
        f"Project: {project.name}\nMethodology: {project.methodology}\nHealth: {health.status}\n"
        f"Tasks: {health.tasks_completed}/{health.tasks_total} complete, {health.tasks_overdue} overdue\n"
        f"Open risks: {health.open_risks} ({health.critical_risks} critical)\n"
        f"Delay probability: {int(health.delay_probability * 100)}%\n"
        f"Top risks: {'; '.join(r.title for r in risks[:5]) or 'none'}"
    )
    response = await llm.chat(
        system_prompt="TASK: status_report\nYou are Atlas, an AI project coordinator. Produce a concise executive status update.",
        messages=[{"role": "user", "content": context}],
    )
    return response["content"]
