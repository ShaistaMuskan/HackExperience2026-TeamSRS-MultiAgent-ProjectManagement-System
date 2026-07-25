"""
REAL Microsoft Teams client using Microsoft Graph.

>>> WHERE THIS PLUGS IN <<<
docs/architecture/azure-foundry-m365-integration-guide.md
  - Section 2.3: ChannelMessage.Send, Chat.ReadWrite, OnlineMeetings.ReadWrite permissions
  - Section 2.5: registering the "AI PM Bot" and posting Adaptive Cards for approvals

pip install msgraph-sdk azure-identity
"""
from __future__ import annotations
from datetime import datetime
from typing import Any

from app.integrations.interfaces import TeamsClient
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("azure.teams")


class GraphTeamsClient(TeamsClient):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = None  # TODO(integration-guide §2.4): same GraphServiceClient as GraphPlannerClient
        logger.warning(
            "GraphTeamsClient instantiated without a live Graph SDK client. "
            "Follow integration guide Section 2 before using in production."
        )

    async def create_channel(self, team_id: str, name: str, description: str = "") -> dict[str, Any]:
        # TODO: POST /teams/{team-id}/channels
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.4/2.5")

    async def send_message(self, channel_id: str, message: str) -> dict[str, Any]:
        # TODO: POST /teams/{team-id}/channels/{channel-id}/messages
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.4/2.5")

    async def send_adaptive_card(self, channel_id: str, card_payload: dict[str, Any]) -> dict[str, Any]:
        # TODO: POST .../messages with body.contentType="html" and an attachment of
        # contentType "application/vnd.microsoft.card.adaptive" - see Section 2.5 for the
        # Approval Card JSON template used by the Human Approval Agent.
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.5")

    async def schedule_meeting(
        self, subject: str, attendees: list[str], start: datetime, end: datetime, body: str = "",
    ) -> dict[str, Any]:
        # TODO: POST /me/onlineMeetings  (or /users/{id}/events with isOnlineMeeting=true)
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.4")
