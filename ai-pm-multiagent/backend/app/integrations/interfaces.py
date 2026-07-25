"""
Abstract interfaces (ports) for every enterprise integration the agents depend on.

Design pattern: Adapter / Ports & Adapters (hexagonal architecture).
Agents and tools NEVER import a concrete client directly - they depend on these
interfaces, which are resolved at runtime by app/core/config.py via
`USE_MOCK_INTEGRATIONS`.

  USE_MOCK_INTEGRATIONS=true   -> app/integrations/mock/*      (works today, no credentials)
  USE_MOCK_INTEGRATIONS=false  -> app/integrations/azure/*     (real Microsoft Graph / Azure SDKs)

See docs/architecture/azure-foundry-m365-integration-guide.md for the exact,
step-by-step Azure AI Foundry + Microsoft 365 setup required before flipping
this flag to `false` in any environment.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional


class PlannerClient(ABC):
    """Microsoft Planner integration (Microsoft Graph `planner` resource)."""

    @abstractmethod
    async def create_plan(self, project_id: str, title: str, owner_group_id: Optional[str] = None) -> dict[str, Any]:
        ...

    @abstractmethod
    async def create_bucket(self, plan_id: str, name: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def create_task(
        self, plan_id: str, bucket_id: str, title: str,
        assignee_ids: list[str], due_date: Optional[datetime], priority: str,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    async def update_task(self, task_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def get_tasks(self, plan_id: str) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def delete_task(self, task_id: str) -> bool:
        ...


class TeamsClient(ABC):
    """Microsoft Teams integration (Microsoft Graph `chatMessage` / `team` resources)."""

    @abstractmethod
    async def create_channel(self, team_id: str, name: str, description: str = "") -> dict[str, Any]:
        ...

    @abstractmethod
    async def send_message(self, channel_id: str, message: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def send_adaptive_card(self, channel_id: str, card_payload: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def schedule_meeting(
        self, subject: str, attendees: list[str], start: datetime, end: datetime, body: str = "",
    ) -> dict[str, Any]:
        ...


class OutlookClient(ABC):
    """Outlook Mail / Calendar integration (Microsoft Graph `me/events`, `me/sendMail`)."""

    @abstractmethod
    async def send_email(self, to: list[str], subject: str, body: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def create_calendar_event(
        self, subject: str, attendees: list[str], start: datetime, end: datetime,
    ) -> dict[str, Any]:
        ...


class SharePointClient(ABC):
    """SharePoint integration (Microsoft Graph `sites/drives` resource)."""

    @abstractmethod
    async def create_project_folder(self, project_name: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def upload_document(self, folder_url: str, filename: str, content_bytes: bytes) -> dict[str, Any]:
        ...


class SearchClient(ABC):
    """RAG retrieval - Azure AI Search."""

    @abstractmethod
    async def index_document(self, doc_id: str, content: str, metadata: dict[str, Any]) -> None:
        ...

    @abstractmethod
    async def search(self, query: str, top_k: int = 5, filters: Optional[str] = None) -> list[dict[str, Any]]:
        ...


class LLMClient(ABC):
    """Reasoning backend - Azure AI Foundry Agent Service / Azure OpenAI."""

    @abstractmethod
    async def chat(
        self, system_prompt: str, messages: list[dict[str, str]],
        tools: Optional[list[dict[str, Any]]] = None, temperature: float = 0.2,
    ) -> dict[str, Any]:
        """Returns {'content': str, 'tool_calls': [...] }"""
        ...


class BlobStorageClient(ABC):
    """Azure Blob Storage - raw project brief / document ingestion."""

    @abstractmethod
    async def upload_file(self, container: str, blob_name: str, content_bytes: bytes) -> str:
        """Returns blob URL."""
        ...

    @abstractmethod
    async def download_file(self, container: str, blob_name: str) -> bytes:
        ...


class SecretsClient(ABC):
    """Azure Key Vault - centralized secrets."""

    @abstractmethod
    def get_secret(self, name: str) -> str:
        ...
