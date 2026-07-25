"""
In-memory stand-in for Microsoft Planner via Microsoft Graph.
Behaves like the real Graph API shape (plannerPlan / plannerBucket / plannerTask)
so swapping in app/integrations/azure/graph_planner_client.py is a drop-in change.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from app.integrations.interfaces import PlannerClient
from app.core.logging import get_logger

logger = get_logger("mock.planner")


class MockPlannerClient(PlannerClient):
    def __init__(self) -> None:
        self.plans: dict[str, dict[str, Any]] = {}
        self.buckets: dict[str, dict[str, Any]] = {}
        self.tasks: dict[str, dict[str, Any]] = {}

    async def create_plan(self, project_id: str, title: str, owner_group_id: Optional[str] = None) -> dict[str, Any]:
        plan_id = f"plan_{uuid4().hex[:8]}"
        plan = {"id": plan_id, "project_id": project_id, "title": title, "owner_group_id": owner_group_id}
        self.plans[plan_id] = plan
        logger.info(f"[MOCK PLANNER] created plan '{title}' ({plan_id}) for project {project_id}")
        return plan

    async def create_bucket(self, plan_id: str, name: str) -> dict[str, Any]:
        bucket_id = f"bucket_{uuid4().hex[:8]}"
        bucket = {"id": bucket_id, "plan_id": plan_id, "name": name}
        self.buckets[bucket_id] = bucket
        logger.info(f"[MOCK PLANNER] created bucket '{name}' ({bucket_id}) in plan {plan_id}")
        return bucket

    async def create_task(
        self, plan_id: str, bucket_id: str, title: str,
        assignee_ids: list[str], due_date: Optional[datetime], priority: str,
    ) -> dict[str, Any]:
        task_id = f"ptask_{uuid4().hex[:8]}"
        task = {
            "id": task_id, "plan_id": plan_id, "bucket_id": bucket_id, "title": title,
            "assignee_ids": assignee_ids, "due_date_time": due_date.isoformat() if due_date else None,
            "priority": priority, "percent_complete": 0,
        }
        self.tasks[task_id] = task
        logger.info(f"[MOCK PLANNER] created task '{title}' ({task_id}) due={due_date} priority={priority}")
        return task

    async def update_task(self, task_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        if task_id not in self.tasks:
            raise KeyError(f"Planner task {task_id} not found")
        self.tasks[task_id].update(updates)
        logger.info(f"[MOCK PLANNER] updated task {task_id} with {updates}")
        return self.tasks[task_id]

    async def get_tasks(self, plan_id: str) -> list[dict[str, Any]]:
        return [t for t in self.tasks.values() if t["plan_id"] == plan_id]

    async def delete_task(self, task_id: str) -> bool:
        return self.tasks.pop(task_id, None) is not None
