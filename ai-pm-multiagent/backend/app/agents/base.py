"""Shared agent base: memory access, event publishing, tool-call dispatch."""
from __future__ import annotations
from typing import Any, Callable

from app.memory import get_memory_store, MemoryStore
from app.orchestration import get_event_bus, Event, EventBus
from app.core.logging import get_logger


class BaseAgent:
    agent_id: str = "base_agent"

    def __init__(self) -> None:
        self.memory: MemoryStore = get_memory_store()
        self.bus: EventBus = get_event_bus()
        self.logger = get_logger(f"agent.{self.agent_id}")
        self._tool_registry: dict[str, Callable] = {}

    def register_tool(self, name: str, fn: Callable) -> None:
        self._tool_registry[name] = fn

    async def dispatch_tool_call(self, name: str, arguments: dict[str, Any]) -> Any:
        """Routes a Foundry-Agent-style tool_call {name, arguments} to the bound Python callable.
        Used when USE_MOCK_INTEGRATIONS=false and the real Azure AI Foundry Agent decides which
        tool to invoke - see docs/architecture/azure-foundry-m365-integration-guide.md Section 3.5."""
        if name not in self._tool_registry:
            raise KeyError(f"Agent {self.agent_id} has no tool registered for '{name}'")
        fn = self._tool_registry[name]
        self.logger.info(f"Dispatching tool_call '{name}' with args={arguments}")
        result = fn(**arguments)
        if hasattr(result, "__await__"):
            result = await result
        return result

    async def emit(self, event_type: str, project_id: str, payload: dict[str, Any]) -> None:
        await self.bus.publish(Event(type=event_type, project_id=project_id, payload=payload, source_agent=self.agent_id))

    def remember(self, project_id: str, kind: str, content: dict[str, Any]) -> None:
        self.memory.record_decision(self.agent_id, project_id, kind, content)
