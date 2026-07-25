"""Request/response DTOs for the API layer (kept separate from domain Pydantic models)."""
from __future__ import annotations
from typing import Optional, Any
from pydantic import BaseModel


class IngestBriefRequest(BaseModel):
    project_name: str
    source_filename: str = "brief.txt"
    source_type: str = "text"
    raw_text: str
    uploaded_by: str = "demo-pm@contoso.com"


class ApprovalDecisionRequest(BaseModel):
    decision: str  # "approved" | "rejected"
    reviewer: str
    reason: str = ""


class AssignTaskRequest(BaseModel):
    task_id: str
    resource_id: str


class ProposeReassignmentRequest(BaseModel):
    task_id: str
    resource_id: str
    reason: str = "Sentinel-detected resource unavailability"
