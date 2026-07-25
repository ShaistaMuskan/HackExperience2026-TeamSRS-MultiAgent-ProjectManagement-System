from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class Sprint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    name: str
    sprint_number: int
    start_date: datetime
    end_date: datetime
    goal: str = ""
    task_ids: list[str] = Field(default_factory=list)
    committed_points: Optional[int] = None
    completed_points: Optional[int] = None
    completion_probability: Optional[float] = Field(default=None, ge=0, le=1)
