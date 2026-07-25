from __future__ import annotations
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict

from .enums import DependencyType


class Dependency(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    predecessor_task_id: str
    successor_task_id: str
    dependency_type: DependencyType = DependencyType.FINISH_TO_START
    lag_days: float = 0
    is_violated: bool = False

    model_config = ConfigDict(use_enum_values=True)
