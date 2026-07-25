from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict

from .enums import MethodologyType, PhaseType, HealthStatus


class ProjectBrief(BaseModel):
    """Raw input ingested by Atlas before planning begins."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_filename: str
    source_type: str = Field(description="pdf | docx | txt | json | email")
    blob_url: Optional[str] = None
    raw_text: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectPhase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    phase_type: PhaseType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: str = ""


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    brief_id: Optional[str] = None
    methodology: Optional[MethodologyType] = None
    methodology_rationale: Optional[str] = None
    complexity_score: Optional[float] = Field(
        default=None, ge=0, le=1, description="0=simple .. 1=highly complex"
    )
    sponsor: Optional[str] = None
    project_manager: Optional[str] = None
    start_date: Optional[datetime] = None
    target_end_date: Optional[datetime] = None
    phases: list[ProjectPhase] = Field(default_factory=list)
    health: HealthStatus = HealthStatus.ON_TRACK
    planner_plan_id: Optional[str] = None
    teams_channel_id: Optional[str] = None
    sharepoint_folder_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(use_enum_values=True)
