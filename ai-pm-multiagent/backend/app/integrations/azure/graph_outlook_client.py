"""
REAL Outlook Mail/Calendar client using Microsoft Graph.
See docs/architecture/azure-foundry-m365-integration-guide.md Section 2.3
(Mail.Send, Calendars.ReadWrite permissions).
"""
from __future__ import annotations
from datetime import datetime
from typing import Any

from app.integrations.interfaces import OutlookClient
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("azure.outlook")


class GraphOutlookClient(OutlookClient):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = None  # TODO(integration-guide §2.4)

    async def send_email(self, to: list[str], subject: str, body: str) -> dict[str, Any]:
        # TODO: POST /me/sendMail or /users/{id}/sendMail
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.4")

    async def create_calendar_event(
        self, subject: str, attendees: list[str], start: datetime, end: datetime,
    ) -> dict[str, Any]:
        # TODO: POST /me/events
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.4")
