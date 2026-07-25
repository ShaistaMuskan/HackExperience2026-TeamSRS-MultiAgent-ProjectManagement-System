from __future__ import annotations
from typing import Any
from uuid import uuid4

from app.integrations.interfaces import SharePointClient
from app.core.logging import get_logger

logger = get_logger("mock.sharepoint")


class MockSharePointClient(SharePointClient):
    def __init__(self) -> None:
        self.folders: dict[str, dict[str, Any]] = {}
        self.documents: list[dict[str, Any]] = []

    async def create_project_folder(self, project_name: str) -> dict[str, Any]:
        folder_id = f"folder_{uuid4().hex[:8]}"
        url = f"https://contoso.sharepoint.com/sites/PMO/Shared%20Documents/{project_name.replace(' ', '%20')}"
        folder = {"id": folder_id, "name": project_name, "url": url}
        self.folders[folder_id] = folder
        logger.info(f"[MOCK SHAREPOINT] created project folder '{project_name}' -> {url}")
        return folder

    async def upload_document(self, folder_url: str, filename: str, content_bytes: bytes) -> dict[str, Any]:
        doc = {"id": f"doc_{uuid4().hex[:8]}", "folder_url": folder_url, "filename": filename, "size": len(content_bytes)}
        self.documents.append(doc)
        logger.info(f"[MOCK SHAREPOINT] uploaded '{filename}' ({len(content_bytes)} bytes) to {folder_url}")
        return doc
