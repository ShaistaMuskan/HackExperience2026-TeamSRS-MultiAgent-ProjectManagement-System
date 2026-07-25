"""Tool: Microsoft Teams actions - notifications, adaptive approval cards, meetings."""
from __future__ import annotations
from datetime import datetime

from app.core.config import get_teams_client
from app.core.logging import get_logger
from app.db import get_repository
from app.models import Notification, ApprovalRequest

logger = get_logger("tools.teams")


async def create_channel(team_id: str, name: str, description: str = "") -> dict:
    client = get_teams_client()
    return await client.create_channel(team_id, name, description)


async def send_teams_message(project_id: str, channel_id: str, message: str, sent_by_agent: str) -> Notification:
    client = get_teams_client()
    raw = await client.send_message(channel_id, message)
    notification = Notification(
        project_id=project_id, channel="teams", teams_channel_id=channel_id,
        title="Teams Notification", message=message, sent_by_agent=sent_by_agent, delivered=True,
    )
    get_repository().save_notification(notification)
    return notification


def build_approval_card(approval: ApprovalRequest) -> dict:
    """Adaptive Card JSON (v1.5 schema) for a Human Approval request."""
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5",
        "title": approval.title,
        "body": [
            {"type": "TextBlock", "text": approval.title, "weight": "Bolder", "size": "Medium"},
            {"type": "TextBlock", "text": approval.description, "wrap": True},
            {"type": "FactSet", "facts": [
                {"title": "Action type", "value": approval.action_type},
                {"title": "Requested by", "value": approval.requested_by_agent},
                {"title": "Status", "value": approval.status},
            ]},
        ],
        "actions": [
            {"type": "Action.Submit", "title": "Approve", "data": {"approval_id": approval.id, "decision": "approved"}},
            {"type": "Action.Submit", "title": "Reject", "data": {"approval_id": approval.id, "decision": "rejected"}},
        ],
    }


async def send_approval_card(project_id: str, channel_id: str, approval: ApprovalRequest, sent_by_agent: str) -> Notification:
    client = get_teams_client()
    card = build_approval_card(approval)
    raw = await client.send_adaptive_card(channel_id, card)
    approval.teams_card_id = raw["id"]
    notification = Notification(
        project_id=project_id, channel="teams", teams_channel_id=channel_id,
        title=approval.title, message=approval.description, is_adaptive_card=True,
        card_payload=card, sent_by_agent=sent_by_agent, delivered=True,
    )
    get_repository().save_notification(notification)
    return notification


async def schedule_meeting(subject: str, attendees: list[str], start: datetime, end: datetime, body: str = "") -> dict:
    client = get_teams_client()
    return await client.schedule_meeting(subject, attendees, start, end, body)
