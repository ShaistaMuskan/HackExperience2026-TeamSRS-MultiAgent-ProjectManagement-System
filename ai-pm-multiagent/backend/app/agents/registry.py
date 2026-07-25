"""Process-wide singleton instances of each agent, wired together once at startup."""
from __future__ import annotations
from functools import lru_cache

from app.agents.atlas import AtlasAgent
from app.agents.sentinel import SentinelAgent
from app.agents.human_approval import HumanApprovalAgent
from app.agents.orchestrator import OrchestratorAgent


@lru_cache
def get_atlas() -> AtlasAgent:
    return AtlasAgent()


@lru_cache
def get_sentinel() -> SentinelAgent:
    return SentinelAgent()


@lru_cache
def get_human_approval() -> HumanApprovalAgent:
    return HumanApprovalAgent()


@lru_cache
def get_orchestrator() -> OrchestratorAgent:
    return OrchestratorAgent(sentinel=get_sentinel(), human_approval=get_human_approval())
