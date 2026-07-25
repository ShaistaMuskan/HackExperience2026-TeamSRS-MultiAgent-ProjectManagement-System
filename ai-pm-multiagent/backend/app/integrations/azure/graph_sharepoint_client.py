"""
REAL SharePoint client using Microsoft Graph (Sites.ReadWrite.All).
See docs/architecture/azure-foundry-m365-integration-guide.md Section 2.3 & 2.6.
"""
from __future__ import annotations
from typing import Any

from app.integrations.interfaces import SharePointClient
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("azure.sharepoint")


class GraphSharePointClient(SharePointClient):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = None  # TODO(integration-guide §2.4)

    async def create_project_folder(self, project_name: str) -> dict[str, Any]:
        # TODO: POST /sites/{site-id}/drive/root:/{project_name}:/  (special "create folder" pattern)
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.6")

    async def upload_document(self, folder_url: str, filename: str, content_bytes: bytes) -> dict[str, Any]:
        # TODO: PUT /sites/{site-id}/drive/root:/{path}/{filename}:/content
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.6")
