"""
Agent memory persistence.

Hackathon MVP: in-process dict store (fast, zero setup).
Post-hackathon: swap for Cosmos DB / PostgreSQL (see docs SRS Section "Database Schema" -
table `agent_memory` maps 1:1 onto AgentMemory below) without changing the public API.
"""
from __future__ import annotations
from functools import lru_cache
from typing import Any, Optional

from app.models import AgentMemory, MemoryEntry
from app.core.logging import get_logger

logger = get_logger("memory.store")


class MemoryStore:
    def __init__(self) -> None:
        self._memories: dict[tuple[str, str], AgentMemory] = {}

    def _key(self, agent_id: str, project_id: str) -> tuple[str, str]:
        return (agent_id, project_id)

    def get_or_create(self, agent_id: str, project_id: str) -> AgentMemory:
        key = self._key(agent_id, project_id)
        if key not in self._memories:
            self._memories[key] = AgentMemory(agent_id=agent_id, project_id=project_id)
            logger.info(f"Created new memory for agent={agent_id} project={project_id}")
        return self._memories[key]

    def save(self, memory: AgentMemory) -> None:
        self._memories[self._key(memory.agent_id, memory.project_id)] = memory

    def record_decision(self, agent_id: str, project_id: str, kind: str, content: dict[str, Any]) -> MemoryEntry:
        memory = self.get_or_create(agent_id, project_id)
        entry = MemoryEntry(agent_id=agent_id, project_id=project_id, kind=kind, content=content)
        memory.decisions.append(entry)
        memory.current_state.update({"last_decision_kind": kind})
        self.save(memory)
        return entry

    def record_conversation(self, agent_id: str, project_id: str, role: str, content: str) -> None:
        memory = self.get_or_create(agent_id, project_id)
        memory.conversation_log.append({"role": role, "content": content})
        self.save(memory)

    def all_for_project(self, project_id: str) -> list[AgentMemory]:
        return [m for (aid, pid), m in self._memories.items() if pid == project_id]


@lru_cache
def get_memory_store() -> MemoryStore:
    return MemoryStore()
