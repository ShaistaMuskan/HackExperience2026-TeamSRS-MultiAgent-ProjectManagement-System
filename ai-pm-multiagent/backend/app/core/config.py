"""
Central configuration + integration client factory.

The master flag for local/demo vs production:

    USE_MOCK_INTEGRATIONS=true   (default) -> everything runs in-memory, no Azure/M365 needed
    USE_MOCK_INTEGRATIONS=false             -> real Microsoft Graph / Azure SDK clients

Per-service overrides let you go real one integration at a time (e.g. wire up
just the LLM while Planner/Teams/SharePoint/Search/Blob/Secrets stay mocked
until you've implemented/provisioned those too). Leave an override unset to
inherit the master flag; set it explicitly to pin that one service either way:

    USE_MOCK_LLM=false          # only the reasoning backend goes real
    USE_MOCK_PLANNER=true       # ...while Planner stays mocked, overriding a master `false`

See docs/architecture/azure-foundry-m365-integration-guide.md for what has to
exist in your Azure subscription + Microsoft 365 tenant before flipping any of
these to `false`.
"""
from __future__ import annotations
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.integrations.interfaces import (
    PlannerClient, TeamsClient, OutlookClient, SharePointClient,
    SearchClient, LLMClient, BlobStorageClient, SecretsClient,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AI PM Multi-Agent System"
    environment: str = "local"
    use_mock_integrations: bool = True

    # Per-service overrides (None = inherit use_mock_integrations above)
    use_mock_planner: Optional[bool] = None
    use_mock_teams: Optional[bool] = None
    use_mock_outlook: Optional[bool] = None
    use_mock_sharepoint: Optional[bool] = None
    use_mock_search: Optional[bool] = None
    use_mock_llm: Optional[bool] = None
    use_mock_blob: Optional[bool] = None
    use_mock_secrets: Optional[bool] = None

    # --- Microsoft Entra ID / Graph ---
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""
    m365_group_id: str = ""
    m365_team_id: str = ""

    # --- Azure AI Foundry / Azure OpenAI ---
    azure_ai_foundry_project_endpoint: str = ""
    foundry_agent_id: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment_name: str = "gpt-5-mini"
    # Separate deployment from the chat model above - embedding models are
    # deployed independently in Foundry. Optional: if left blank, the real
    # Search client falls back to keyword-only indexing/search (no vectors).
    azure_openai_embedding_deployment: str = "text-embedding-3-large"

    # --- Azure AI Search ---
    azure_search_endpoint: str = ""
    azure_search_api_key: str = ""
    azure_search_index_name: str = "pm-knowledge-base"

    # --- Azure Storage ---
    azure_storage_account_url: str = ""
    azure_storage_container_briefs: str = "project-briefs"

    # --- Azure Key Vault ---
    key_vault_url: str = ""

    # --- App / DB ---
    database_url: str = "sqlite+aiosqlite:///./ai_pm.db"
    secret_key: str = "dev-only-change-me"
    sentinel_poll_interval_seconds: int = 30
    cors_origins: str = "http://localhost:5173,http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _is_mock(settings: Settings, override: Optional[bool]) -> bool:
    """Per-service override wins if set; otherwise inherit the master flag."""
    return settings.use_mock_integrations if override is None else override


def get_integration_status() -> dict[str, dict[str, str]]:
    """
    Reports whether each integration is currently backed by its mock or real
    client, without instantiating either (so this is safe/cheap to call from
    an API route on every request - e.g. for a dashboard status indicator).
    """
    settings = get_settings()
    services = {
        "llm": ("Reasoning (Azure OpenAI/Foundry)", settings.use_mock_llm),
        "planner": ("Microsoft Planner", settings.use_mock_planner),
        "teams": ("Microsoft Teams", settings.use_mock_teams),
        "outlook": ("Outlook", settings.use_mock_outlook),
        "sharepoint": ("SharePoint", settings.use_mock_sharepoint),
        "search": ("Azure AI Search (RAG)", settings.use_mock_search),
        "blob": ("Azure Blob Storage", settings.use_mock_blob),
        "secrets": ("Azure Key Vault", settings.use_mock_secrets),
    }
    return {
        key: {"label": label, "status": "mock" if _is_mock(settings, override) else "live"}
        for key, (label, override) in services.items()
    }


# --------------------------------------------------------------------------
# Integration client factory (the adapter switch)
# --------------------------------------------------------------------------
@lru_cache
def get_planner_client() -> PlannerClient:
    settings = get_settings()
    if _is_mock(settings, settings.use_mock_planner):
        from app.integrations.mock.mock_planner_client import MockPlannerClient
        return MockPlannerClient()
    from app.integrations.azure.graph_planner_client import GraphPlannerClient
    return GraphPlannerClient()


@lru_cache
def get_teams_client() -> TeamsClient:
    settings = get_settings()
    if _is_mock(settings, settings.use_mock_teams):
        from app.integrations.mock.mock_teams_client import MockTeamsClient
        return MockTeamsClient()
    from app.integrations.azure.graph_teams_client import GraphTeamsClient
    return GraphTeamsClient()


@lru_cache
def get_outlook_client() -> OutlookClient:
    settings = get_settings()
    if _is_mock(settings, settings.use_mock_outlook):
        from app.integrations.mock.mock_outlook_client import MockOutlookClient
        return MockOutlookClient()
    from app.integrations.azure.graph_outlook_client import GraphOutlookClient
    return GraphOutlookClient()


@lru_cache
def get_sharepoint_client() -> SharePointClient:
    settings = get_settings()
    if _is_mock(settings, settings.use_mock_sharepoint):
        from app.integrations.mock.mock_sharepoint_client import MockSharePointClient
        return MockSharePointClient()
    from app.integrations.azure.graph_sharepoint_client import GraphSharePointClient
    return GraphSharePointClient()


@lru_cache
def get_search_client() -> SearchClient:
    settings = get_settings()
    if _is_mock(settings, settings.use_mock_search):
        from app.integrations.mock.mock_search_client import MockSearchClient
        return MockSearchClient()
    from app.integrations.azure.azure_search_client import AzureSearchClient
    return AzureSearchClient()


@lru_cache
def get_llm_client() -> LLMClient:
    settings = get_settings()
    if _is_mock(settings, settings.use_mock_llm):
        from app.integrations.mock.mock_llm_client import MockLLMClient
        return MockLLMClient()
    from app.integrations.azure.azure_openai_client import AzureFoundryLLMClient
    return AzureFoundryLLMClient()


@lru_cache
def get_blob_client() -> BlobStorageClient:
    settings = get_settings()
    if _is_mock(settings, settings.use_mock_blob):
        from app.integrations.mock.mock_blob_client import MockBlobStorageClient
        return MockBlobStorageClient()
    from app.integrations.azure.blob_storage_client import AzureBlobStorageClient
    return AzureBlobStorageClient()


@lru_cache
def get_secrets_client() -> SecretsClient:
    settings = get_settings()
    if _is_mock(settings, settings.use_mock_secrets):
        from app.integrations.mock.mock_secrets_client import MockSecretsClient
        return MockSecretsClient()
    from app.integrations.azure.key_vault_client import AzureKeyVaultClient
    return AzureKeyVaultClient()
