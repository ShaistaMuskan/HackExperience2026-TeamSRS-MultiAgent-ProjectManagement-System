from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict

from .enums import TaskStatus, Priority


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    epic_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.NOT_STARTED
    priority: Priority = Priority.MEDIUM
    assignee: Optional[str] = None
    estimated_hours: Optional[float] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    wbs_code: Optional[str] = Field(default=None, description="e.g. 1.2.3")
    dependency_ids: list[str] = Field(default_factory=list)
    planner_task_id: Optional[str] = None
    sprint_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(use_enum_values=True)


class UserStory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    epic_id: str
    title: str
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    story_points: Optional[int] = None
    task_ids: list[str] = Field(default_factory=list)


class Epic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    title: str
    description: str = ""
    phase_id: Optional[str] = None
    user_story_ids: list[str] = Field(default_factory=list)
