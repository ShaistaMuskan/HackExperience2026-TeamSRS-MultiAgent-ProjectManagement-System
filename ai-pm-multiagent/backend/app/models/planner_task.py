from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict

from .enums import Priority


class PlannerBucket(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    plan_id: str
    name: str
    order_hint: str = ""


class PlannerTask(BaseModel):
    """Mirrors the shape of a Microsoft Planner task (Graph API `plannerTask`)."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    plan_id: str
    bucket_id: str
    title: str
    assignee_ids: list[str] = Field(default_factory=list)
    priority: Priority = Priority.MEDIUM
    percent_complete: int = 0
    start_date_time: Optional[datetime] = None
    due_date_time: Optional[datetime] = None
    checklist: list[str] = Field(default_factory=list)
    internal_task_id: Optional[str] = Field(default=None, description="link back to our Task.id")

    model_config = ConfigDict(use_enum_values=True)


class PlannerPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    title: str
    owner_group_id: Optional[str] = None
    buckets: list[PlannerBucket] = Field(default_factory=list)
