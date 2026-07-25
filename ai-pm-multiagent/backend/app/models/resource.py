from __future__ import annotations
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class Resource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    email: str
    role: str
    skills: list[str] = Field(default_factory=list)
    weekly_capacity_hours: float = 40
    allocated_hours: float = 0
    availability_start: Optional[str] = None
    availability_end: Optional[str] = None
    is_available: bool = True

    @property
    def utilization(self) -> float:
        if self.weekly_capacity_hours == 0:
            return 0.0
        return round(self.allocated_hours / self.weekly_capacity_hours, 2)
