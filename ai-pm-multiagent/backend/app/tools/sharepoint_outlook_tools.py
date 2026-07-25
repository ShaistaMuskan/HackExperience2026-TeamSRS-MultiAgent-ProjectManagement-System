"""Tool: SharePoint project folders + Outlook email/calendar actions."""
from __future__ import annotations
from datetime import datetime

from app.core.config import get_sharepoint_client, get_outlook_client
from app.core.logging import get_logger

logger = get_logger("tools.sharepoint_outlook")


async def create_sharepoint_project_folder(project_name: str) -> dict:
    client = get_sharepoint_client()
    return await client.create_project_folder(project_name)


async def upload_document(folder_url: str, filename: str, content_bytes: bytes) -> dict:
    client = get_sharepoint_client()
    return await client.upload_document(folder_url, filename, content_bytes)


async def send_email_notification(to: list[str], subject: str, body: str) -> dict:
    client = get_outlook_client()
    return await client.send_email(to, subject, body)


async def schedule_kickoff_meeting(subject: str, attendees: list[str], start: datetime, end: datetime) -> dict:
    client = get_outlook_client()
    return await client.create_calendar_event(subject, attendees, start, end)
