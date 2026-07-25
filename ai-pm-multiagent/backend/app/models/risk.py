from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict

from .enums import RiskSeverity, RiskCategory


class Risk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    title: str
    description: str = ""
    category: RiskCategory
    severity: RiskSeverity
    probability: float = Field(ge=0, le=1, description="Likelihood of occurring")
    impact_score: float = Field(ge=0, le=1)
    detected_by: str = Field(default="sentinel", description="agent id that detected it")
    related_task_ids: list[str] = Field(default_factory=list)
    mitigation_plan: Optional[str] = None
    requires_approval: bool = False
    approval_id: Optional[str] = None
    resolved: bool = False
    detected_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(use_enum_values=True)

    @property
    def risk_score(self) -> float:
        return round(self.probability * self.impact_score, 3)


class RiskRegister(BaseModel):
    project_id: str
    risks: list[Risk] = Field(default_factory=list)

    def open_risks(self) -> list[Risk]:
        return [r for r in self.risks if not r.resolved]

    def critical_risks(self) -> list[Risk]:
        return [r for r in self.risks if r.severity == RiskSeverity.CRITICAL and not r.resolved]
