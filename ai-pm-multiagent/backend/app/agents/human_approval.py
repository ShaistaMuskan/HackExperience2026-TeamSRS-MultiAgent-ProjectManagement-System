"""
Human Approval Agent.

Gatekeeper for actions the spec marks as requiring a human: deadline changes,
resource reassignment, task deletion, escalations, budget changes, and large
schedule modifications. Any other agent that wants to take one of these
actions must go through `request_approval` instead of calling the tool directly.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.db import get_repository
from app.models import ApprovalRequest, ApprovalActionType, ApprovalStatus
from app.tools import teams_tools, planner_tools


class HumanApprovalAgent(BaseAgent):
    agent_id = "human_approval"

    def __init__(self) -> None:
        super().__init__()
        self.repo = get_repository()

    async def request_approval(
        self, project_id: str, requested_by_agent: str, action_type: ApprovalActionType,
        title: str, description: str, payload: dict[str, Any],
    ) -> ApprovalRequest:
        approval = ApprovalRequest(
            project_id=project_id, requested_by_agent=requested_by_agent, action_type=action_type,
            title=title, description=description, payload=payload,
        )
        self.repo.save_approval(approval)

        project = self.repo.get_project(project_id)
        channel_id = project.teams_channel_id if project else "channel_default"
        await teams_tools.send_approval_card(project_id, channel_id, approval, sent_by_agent=self.agent_id)

        await self.emit("approval.requested", project_id, {"approval_id": approval.id, "action_type": action_type})
        self.remember(project_id, "approval", {"approval_id": approval.id, "status": "pending", "title": title})
        return approval

    async def decide(self, approval_id: str, decision: str, reviewer: str, reason: str = "") -> ApprovalRequest:
        approval = self.repo.get_approval(approval_id)
        if not approval:
            raise KeyError(f"Unknown approval {approval_id}")

        approval.status = ApprovalStatus.APPROVED if decision == "approved" else ApprovalStatus.REJECTED
        approval.reviewer = reviewer
        approval.decision_reason = reason
        approval.decided_at = datetime.utcnow()
        self.repo.save_approval(approval)

        if approval.status == ApprovalStatus.APPROVED:
            await self._execute(approval)

        project = self.repo.get_project(approval.project_id)
        channel_id = project.teams_channel_id if project else "channel_default"
        await teams_tools.send_teams_message(
            project_id=approval.project_id, channel_id=channel_id,
            message=f"✅ Approval **{approval.title}** was **{approval.status}** by {reviewer}."
                    if approval.status == ApprovalStatus.APPROVED
                    else f"❌ Approval **{approval.title}** was **{approval.status}** by {reviewer}.",
            sent_by_agent=self.agent_id,
        )
        await self.emit("approval.decided", approval.project_id, {"approval_id": approval.id, "status": approval.status})
        self.remember(approval.project_id, "approval", {"approval_id": approval.id, "status": approval.status})
        return approval

    async def _execute(self, approval: ApprovalRequest) -> None:
        """Executes the actual enterprise action now that a human has signed off."""
        payload = approval.payload
        if approval.action_type == ApprovalActionType.REASSIGN_RESOURCE:
            task = self.repo.get_task(payload["task_id"])
            resource = self.repo.get_resource(payload["resource_id"])
            if task and resource:
                planner_tools.assign_task(task, resource)
                self.repo.save_task(task)
                if task.planner_task_id:
                    await planner_tools.update_planner_task(task.planner_task_id, {"assignee_ids": [resource.id]})

        elif approval.action_type == ApprovalActionType.CHANGE_DEADLINE:
            task = self.repo.get_task(payload["task_id"])
            if task:
                task.due_date = datetime.fromisoformat(payload["new_due_date"])
                self.repo.save_task(task)
                if task.planner_task_id:
                    await planner_tools.update_planner_task(task.planner_task_id, {"due_date_time": payload["new_due_date"]})

        elif approval.action_type == ApprovalActionType.DELETE_TASK:
            task = self.repo.get_task(payload["task_id"])
            if task and task.planner_task_id:
                from app.core.config import get_planner_client
                await get_planner_client().delete_task(task.planner_task_id)
            self.repo.tasks.pop(payload["task_id"], None)

        # ESCALATION / BUDGET_CHANGE / SCHEDULE_CHANGE: recorded + notified;
        # downstream execution is project-specific and left to the PM/Orchestrator
        # to route to the appropriate follow-up tool call.
        self.logger.info(f"Executed approved action {approval.action_type} for approval {approval.id}")
