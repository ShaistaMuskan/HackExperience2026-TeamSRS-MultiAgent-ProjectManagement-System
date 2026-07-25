from __future__ import annotations
from datetime import datetime
from typing import Optional, Any
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict

from .enums import ApprovalStatus, ApprovalActionType


class ApprovalRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    requested_by_agent: str
    action_type: ApprovalActionType
    title: str
    description: str
    payload: dict[str, Any] = Field(default_factory=dict, description="Action-specific data needed to execute on approval")
    status: ApprovalStatus = ApprovalStatus.PENDING
    teams_card_id: Optional[str] = None
    reviewer: Optional[str] = None
    decision_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None

    model_config = ConfigDict(use_enum_values=True)
