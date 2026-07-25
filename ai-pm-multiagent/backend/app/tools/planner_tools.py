"""
Tool: Microsoft Planner actions.
Thin, typed wrappers around app.core.config.get_planner_client() so agents
call `create_planner_task(...)` rather than touching the Graph client directly.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional

from app.core.config import get_planner_client
from app.core.logging import get_logger
from app.models import PlannerPlan, PlannerBucket, PlannerTask, Priority, Task, Resource

logger = get_logger("tools.planner")


async def create_plan(project_id: str, title: str, owner_group_id: Optional[str] = None) -> PlannerPlan:
    client = get_planner_client()
    raw = await client.create_plan(project_id=project_id, title=title, owner_group_id=owner_group_id)
    return PlannerPlan(id=raw["id"], project_id=project_id, title=title, owner_group_id=owner_group_id)


async def create_bucket(plan_id: str, name: str) -> PlannerBucket:
    client = get_planner_client()
    raw = await client.create_bucket(plan_id=plan_id, name=name)
    return PlannerBucket(id=raw["id"], plan_id=plan_id, name=name)


async def create_planner_task(
    plan_id: str, bucket_id: str, task: Task, assignees: Optional[list[Resource]] = None,
) -> PlannerTask:
    client = get_planner_client()
    assignee_ids = [r.id for r in (assignees or [])]
    raw = await client.create_task(
        plan_id=plan_id, bucket_id=bucket_id, title=task.title,
        assignee_ids=assignee_ids, due_date=task.due_date, priority=task.priority,
    )
    return PlannerTask(
        id=raw["id"], plan_id=plan_id, bucket_id=bucket_id, title=task.title,
        assignee_ids=assignee_ids, priority=task.priority, due_date_time=task.due_date,
        internal_task_id=task.id,
    )


async def update_planner_task(planner_task_id: str, updates: dict) -> dict:
    client = get_planner_client()
    result = await client.update_task(planner_task_id, updates)
    logger.info(f"Planner task {planner_task_id} updated: {updates}")
    return result


async def get_planner_tasks(plan_id: str) -> list[dict]:
    client = get_planner_client()
    return await client.get_tasks(plan_id)


def assign_task(task: Task, resource: Resource) -> Task:
    """Pure logic: bind a resource to a task and bump its allocated hours."""
    task.assignee = resource.email
    resource.allocated_hours += task.estimated_hours or 0
    return task
