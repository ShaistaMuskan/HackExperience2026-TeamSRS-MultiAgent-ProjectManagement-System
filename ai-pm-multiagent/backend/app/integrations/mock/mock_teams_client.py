from __future__ import annotations
from datetime import datetime
from typing import Any
from uuid import uuid4

from app.integrations.interfaces import TeamsClient
from app.core.logging import get_logger

logger = get_logger("mock.teams")


class MockTeamsClient(TeamsClient):
    def __init__(self) -> None:
        self.channels: dict[str, dict[str, Any]] = {}
        self.messages: list[dict[str, Any]] = []
        self.meetings: list[dict[str, Any]] = []

    async def create_channel(self, team_id: str, name: str, description: str = "") -> dict[str, Any]:
        channel_id = f"channel_{uuid4().hex[:8]}"
        channel = {"id": channel_id, "team_id": team_id, "name": name, "description": description}
        self.channels[channel_id] = channel
        logger.info(f"[MOCK TEAMS] created channel '{name}' ({channel_id})")
        return channel

    async def send_message(self, channel_id: str, message: str) -> dict[str, Any]:
        msg = {"id": f"msg_{uuid4().hex[:8]}", "channel_id": channel_id, "message": message}
        self.messages.append(msg)
        logger.info(f"[MOCK TEAMS -> #{channel_id}] {message}")
        return msg

    async def send_adaptive_card(self, channel_id: str, card_payload: dict[str, Any]) -> dict[str, Any]:
        msg = {"id": f"card_{uuid4().hex[:8]}", "channel_id": channel_id, "card": card_payload}
        self.messages.append(msg)
        logger.info(f"[MOCK TEAMS CARD -> #{channel_id}] {card_payload.get('title', card_payload)}")
        return msg

    async def schedule_meeting(
        self, subject: str, attendees: list[str], start: datetime, end: datetime, body: str = "",
    ) -> dict[str, Any]:
        meeting = {
            "id": f"meeting_{uuid4().hex[:8]}", "subject": subject, "attendees": attendees,
            "start": start.isoformat(), "end": end.isoformat(), "body": body,
            "join_url": "https://teams.microsoft.com/l/meetup-join/mock",
        }
        self.meetings.append(meeting)
        logger.info(f"[MOCK TEAMS] scheduled meeting '{subject}' with {attendees}")
        return meeting
