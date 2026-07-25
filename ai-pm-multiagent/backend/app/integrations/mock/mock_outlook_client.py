from __future__ import annotations
from datetime import datetime
from typing import Any
from uuid import uuid4

from app.integrations.interfaces import OutlookClient
from app.core.logging import get_logger

logger = get_logger("mock.outlook")


class MockOutlookClient(OutlookClient):
    def __init__(self) -> None:
        self.sent_emails: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []

    async def send_email(self, to: list[str], subject: str, body: str) -> dict[str, Any]:
        email = {"id": f"mail_{uuid4().hex[:8]}", "to": to, "subject": subject, "body": body}
        self.sent_emails.append(email)
        logger.info(f"[MOCK OUTLOOK] email to {to}: {subject}")
        return email

    async def create_calendar_event(
        self, subject: str, attendees: list[str], start: datetime, end: datetime,
    ) -> dict[str, Any]:
        event = {
            "id": f"event_{uuid4().hex[:8]}", "subject": subject, "attendees": attendees,
            "start": start.isoformat(), "end": end.isoformat(),
        }
        self.events.append(event)
        logger.info(f"[MOCK OUTLOOK] calendar event '{subject}' with {attendees}")
        return event
