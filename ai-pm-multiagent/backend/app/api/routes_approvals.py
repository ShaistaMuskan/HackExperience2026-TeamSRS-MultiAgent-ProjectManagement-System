"""Human Approval Agent endpoints - the human-in-the-loop gate."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import ApprovalDecisionRequest, ProposeReassignmentRequest
from app.core.security import get_current_user, require_permission, CurrentUser
from app.db import get_repository
from app.agents import get_human_approval
from app.models import ApprovalActionType

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/{project_id}")
async def list_approvals(project_id: str, pending_only: bool = False, user: CurrentUser = Depends(get_current_user)):
    return get_repository().list_approvals(project_id, pending_only=pending_only)


@router.post("/{approval_id}/decide")
async def decide_approval(approval_id: str, req: ApprovalDecisionRequest, user: CurrentUser = Depends(get_current_user)):
    require_permission(user, "approve")
    agent = get_human_approval()
    try:
        return await agent.decide(approval_id, decision=req.decision, reviewer=req.reviewer, reason=req.reason)
    except KeyError as e:
        raise HTTPException(404, str(e))


@router.post("/{project_id}/propose-reassignment", summary="Agent-initiated reassignment proposal (requires human approval)")
async def propose_reassignment(project_id: str, req: ProposeReassignmentRequest, user: CurrentUser = Depends(get_current_user)):
    require_permission(user, "write")
    agent = get_human_approval()
    repo = get_repository()
    task = repo.get_task(req.task_id)
    resource = repo.get_resource(req.resource_id)
    if not task or not resource:
        raise HTTPException(404, "task or resource not found")
    return await agent.request_approval(
        project_id=project_id, requested_by_agent="sentinel", action_type=ApprovalActionType.REASSIGN_RESOURCE,
        title=f"Reassign '{task.title}' to {resource.name}", description=req.reason,
        payload={"task_id": req.task_id, "resource_id": req.resource_id},
    )
