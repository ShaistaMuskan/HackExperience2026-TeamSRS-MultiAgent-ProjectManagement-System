"""
Lightweight async event bus - the backbone of event-driven, multi-agent
communication described in the spec's "Event-Based Workflow" section.

Agents never call each other directly. They publish events
(e.g. "planner.task.created", "sentinel.risk.detected") and the
Workflow Orchestrator Agent (app/agents/orchestrator.py) subscribes to route
them to the right downstream agent. This keeps agents independently
deployable/testable microservices in spirit, even though they run in one
process for the hackathon MVP.
"""
from __future__ import annotations
import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from typing import Any, Awaitable, Callable
from uuid import uuid4

from app.core.logging import get_logger

logger = get_logger("orchestration.event_bus")

Handler = Callable[["Event"], Awaitable[None]]


@dataclass
class Event:
    type: str
    project_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    source_agent: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = defaultdict(list)
        self._history: list[Event] = []

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler {getattr(handler, '__qualname__', handler)} to '{event_type}'")

    async def publish(self, event: Event) -> None:
        self._history.append(event)
        logger.info(f"EVENT [{event.type}] project={event.project_id} source={event.source_agent} payload_keys={list(event.payload.keys())}")
        handlers = self._subscribers.get(event.type, []) + self._subscribers.get("*", [])
        await asyncio.gather(*(h(event) for h in handlers), return_exceptions=False)

    def history(self, project_id: str | None = None) -> list[Event]:
        if project_id:
            return [e for e in self._history if e.project_id == project_id]
        return list(self._history)


@lru_cache
def get_event_bus() -> EventBus:
    return EventBus()
