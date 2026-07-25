from __future__ import annotations
from datetime import datetime
from typing import Optional, Any
from uuid import uuid4
from pydantic import BaseModel, Field


class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    channel: str = Field(description="teams | email | in_app")
    teams_channel_id: Optional[str] = None
    title: str
    message: str
    is_adaptive_card: bool = False
    card_payload: Optional[dict[str, Any]] = None
    sent_by_agent: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    delivered: bool = False
