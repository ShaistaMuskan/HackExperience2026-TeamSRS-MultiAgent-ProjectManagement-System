from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class Milestone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    name: str
    description: str = ""
    due_date: datetime
    is_deliverable: bool = False
    completed: bool = False
    completed_at: Optional[datetime] = None
    dependent_task_ids: list[str] = Field(default_factory=list)
    on_critical_path: bool = False
