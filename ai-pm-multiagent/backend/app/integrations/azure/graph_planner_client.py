"""
REAL Microsoft Planner client using Microsoft Graph.

>>> WHERE THIS PLUGS IN <<<
See docs/architecture/azure-foundry-m365-integration-guide.md
  - Section 2: Entra ID App Registration + Graph API permissions
  - Section 2.3: Tasks.ReadWrite, Group.ReadWrite.All (application permissions)

Required env vars (see .env.example):
  AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, M365_GROUP_ID

Activate by setting USE_MOCK_INTEGRATIONS=false in .env - app/core/config.py
will construct this class instead of MockPlannerClient.

pip install msgraph-sdk azure-identity
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional

from app.integrations.interfaces import PlannerClient
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("azure.planner")


class GraphPlannerClient(PlannerClient):
    def __init__(self) -> None:
        # TODO(integration-guide §2.4): construct the Graph SDK client here, e.g.:
        #
        #   from azure.identity.aio import ClientSecretCredential
        #   from msgraph import GraphServiceClient
        #
        #   settings = get_settings()
        #   credential = ClientSecretCredential(
        #       tenant_id=settings.azure_tenant_id,
        #       client_id=settings.azure_client_id,
        #       client_secret=settings.azure_client_secret,
        #   )
        #   self.client = GraphServiceClient(credentials=credential, scopes=["https://graph.microsoft.com/.default"])
        self.settings = get_settings()
        self.client = None  # populated per integration guide §2.4
        logger.warning(
            "GraphPlannerClient instantiated without a live Graph SDK client. "
            "Follow docs/architecture/azure-foundry-m365-integration-guide.md Section 2 "
            "to wire up real Microsoft Graph calls before using in production."
        )

    async def create_plan(self, project_id: str, title: str, owner_group_id: Optional[str] = None) -> dict[str, Any]:
        # TODO: POST /groups/{group-id}/planner/plans  (Graph SDK: self.client.planner.plans.post(...))
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.4")

    async def create_bucket(self, plan_id: str, name: str) -> dict[str, Any]:
        # TODO: POST /planner/buckets
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.4")

    async def create_task(
        self, plan_id: str, bucket_id: str, title: str,
        assignee_ids: list[str], due_date: Optional[datetime], priority: str,
    ) -> dict[str, Any]:
        # TODO: POST /planner/tasks  (map priority: critical/high/medium/low -> Planner's 1/3/5/9 int scale)
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.4")

    async def update_task(self, task_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        # TODO: PATCH /planner/tasks/{id}  - requires If-Match ETag header from a prior GET
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.4")

    async def get_tasks(self, plan_id: str) -> list[dict[str, Any]]:
        # TODO: GET /planner/plans/{plan-id}/tasks
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.4")

    async def delete_task(self, task_id: str) -> bool:
        # TODO: DELETE /planner/tasks/{id}  - requires If-Match ETag header
        raise NotImplementedError("Wire up Graph API call - see integration guide Section 2.4")
