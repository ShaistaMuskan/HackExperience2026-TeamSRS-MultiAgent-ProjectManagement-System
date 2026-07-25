from __future__ import annotations
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict

from .enums import HealthStatus


class ProjectHealth(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    status: HealthStatus
    schedule_variance_days: float = 0
    tasks_total: int = 0
    tasks_completed: int = 0
    tasks_overdue: int = 0
    open_risks: int = 0
    critical_risks: int = 0
    delay_probability: float = Field(default=0, ge=0, le=1)
    budget_risk_score: float = Field(default=0, ge=0, le=1)
    resource_bottleneck_score: float = Field(default=0, ge=0, le=1)
    summary: str = ""
    computed_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(use_enum_values=True)
