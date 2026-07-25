from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    project_id: str
    kind: str = Field(description="decision | observation | approval | event")
    content: dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentMemory(BaseModel):
    """Per-agent, per-project memory. Backed by memory/memory_store.py."""
    agent_id: str
    project_id: str
    current_state: dict[str, Any] = Field(default_factory=dict)
    completed_task_ids: list[str] = Field(default_factory=list)
    known_risk_ids: list[str] = Field(default_factory=list)
    decisions: list[MemoryEntry] = Field(default_factory=list)
    methodology: Optional[str] = None
    dependency_ids: list[str] = Field(default_factory=list)
    approval_ids: list[str] = Field(default_factory=list)
    conversation_log: list[dict[str, Any]] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
