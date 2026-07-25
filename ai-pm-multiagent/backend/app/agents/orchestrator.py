"""
Workflow Orchestrator Agent.

Coordinates communication between Atlas, Sentinel, and the Human Approval
Agent purely through the event bus (app/orchestration/event_bus.py) - it
holds no domain logic of its own, only routing + cross-agent workflow state.

Example wired here (matches the spec):
  planner.task.updated -> notify Sentinel to recalculate risk
  sentinel.risk.detected (critical) -> ask Human Approval Agent to request approval
  approval.decided (approved) -> re-run Sentinel pass + notify Teams
"""
from __future__ import annotations
from typing import Any

from app.agents.base import BaseAgent
from app.orchestration import Event
from app.models import ApprovalActionType
from app.tools import teams_tools


class OrchestratorAgent(BaseAgent):
    agent_id = "orchestrator"

    def __init__(self, sentinel, human_approval) -> None:
        super().__init__()
        self.sentinel = sentinel
        self.human_approval = human_approval
        self.workflow_state: dict[str, dict[str, Any]] = {}
        self._wire_subscriptions()

    def _wire_subscriptions(self) -> None:
        self.bus.subscribe("atlas.plan.created", self.on_plan_created)
        self.bus.subscribe("planner.task.updated", self.on_planner_task_updated)
        self.bus.subscribe("sentinel.risk.detected", self.on_risk_detected)
        self.bus.subscribe("approval.decided", self.on_approval_decided)

    def _state(self, project_id: str) -> dict[str, Any]:
        return self.workflow_state.setdefault(project_id, {"stage": "new", "events": 0})

    async def on_plan_created(self, event: Event) -> None:
        state = self._state(event.project_id)
        state["stage"] = "planned"
        state["events"] += 1
        self.logger.info(f"[ORCHESTRATOR] project {event.project_id} plan created -> starting Sentinel monitoring")
        await self.sentinel.monitor_project(event.project_id)

    async def on_planner_task_updated(self, event: Event) -> None:
        state = self._state(event.project_id)
        state["events"] += 1
        self.logger.info(f"[ORCHESTRATOR] planner task updated -> recalculating risk for {event.project_id}")
        await self.sentinel.monitor_project(event.project_id)

    async def on_risk_detected(self, event: Event) -> None:
        """
        Critical risks get routed to the Human Approval Agent automatically.

        HIGH-severity risks normally don't (they're logged/mitigation-suggested
        by Sentinel but stop there) - EXCEPT when Sentinel found a concrete,
        single-task reassignment candidate (risk_tools.find_reassignment_candidate).
        That case is deliberately let through at HIGH severity too: it's the
        canonical "engineer went unavailable" scenario from the spec, resource
        conflicts never actually reach CRITICAL under risk_tools.py's rules, and
        the action is safely gated behind a human click either way.

        When there's a candidate, the request is a REASSIGN_RESOURCE action
        instead of a generic ESCALATION - so approving it auto-executes the
        reassignment (see HumanApprovalAgent._execute) and work continues
        without a separate manual propose-reassignment call. Anything
        ambiguous still falls back to ESCALATION, which records the decision
        for the PM to action.
        """
        state = self._state(event.project_id)
        state["events"] += 1
        severity = event.payload.get("severity")
        candidate = event.payload.get("reassignment_candidate")
        if severity != "critical" and not (severity == "high" and candidate):
            return

        if candidate:
            await self.human_approval.request_approval(
                project_id=event.project_id, requested_by_agent="sentinel",
                action_type=ApprovalActionType.REASSIGN_RESOURCE,
                title=f"Reassign task to {candidate['resource_name']} ({event.payload.get('title')})",
                description=event.payload.get("mitigation_suggestion", ""),
                payload={"task_id": candidate["task_id"], "resource_id": candidate["resource_id"]},
            )
        else:
            await self.human_approval.request_approval(
                project_id=event.project_id, requested_by_agent="sentinel",
                action_type=ApprovalActionType.ESCALATION,
                title=f"Critical risk: {event.payload.get('title')}",
                description=event.payload.get("mitigation_suggestion", ""),
                payload={"risk_id": event.payload.get("risk_id")},
            )

    async def on_approval_decided(self, event: Event) -> None:
        state = self._state(event.project_id)
        state["events"] += 1
        if event.payload.get("status") == "approved":
            self.logger.info(f"[ORCHESTRATOR] approval approved -> re-running Sentinel pass for {event.project_id}")
            await self.sentinel.monitor_project(event.project_id)

    def get_state(self, project_id: str) -> dict[str, Any]:
        return self._state(project_id)
