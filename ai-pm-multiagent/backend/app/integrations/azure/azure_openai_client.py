"""
REAL reasoning backend: Azure AI Foundry Agent Service (preferred) or raw
Azure OpenAI chat completions (fallback).

>>> WHERE THIS PLUGS IN <<<
docs/architecture/azure-foundry-m365-integration-guide.md
  - Section 3: Azure AI Foundry / Microsoft Foundry project + model deployment.
    NOTE: gpt-4o and gpt-4o-mini are deprecated for new deployments as of 2026 -
    deploy a current GA model instead (e.g. gpt-5-mini) and set its deployment
    name in AZURE_OPENAI_DEPLOYMENT_NAME. Check the model catalog for whichever
    non-deprecated model is available in your region at deploy time.
  - Section 3.4: Foundry Agent creation with tool/function definitions from
    app/tools/tool_schemas.py
  - Section 3.5: connecting the Foundry Agent's tool-calls back to
    app/tools/*.py implementations

Required env vars: AZURE_AI_FOUNDRY_PROJECT_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_NAME,
                    AZURE_OPENAI_API_KEY (or Entra ID auth - recommended for prod)

pip install azure-ai-projects azure-ai-inference openai azure-identity
"""
from __future__ import annotations
from typing import Any, Optional

from app.integrations.interfaces import LLMClient
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("azure.openai")


class AzureFoundryLLMClient(LLMClient):
    """
    Direct Azure OpenAI chat-completions implementation (integration-guide §3.6,
    "Option B"). This is the recommended path for student/limited-quota
    subscriptions: it needs only one model deployment (no Foundry Agent Service
    threads/runs to provision) and works with either an API key or Entra ID.

    Wiring an Azure AI Foundry Agent Service *agent* instead (Option A, with
    persistent threads and portal-managed tool catalogs) is possible but the
    Foundry portal cannot attach custom function-tool schemas like the ones in
    app/tools/tool_schemas.py - those can only be registered via the Foundry
    SDK/REST API, not portal clicks. Option B reaches the same tool-calling
    behavior with far less setup and is what this class implements.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.azure_openai_endpoint or not self.settings.azure_openai_api_key:
            logger.warning(
                "AzureFoundryLLMClient created with empty endpoint/key - chat() will fail. "
                "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env "
                "(see integration guide Section 3)."
            )
        from openai import AsyncAzureOpenAI

        self.client = AsyncAzureOpenAI(
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_key=self.settings.azure_openai_api_key,
            api_version="2024-10-21",
        )
        # None = unknown yet (try once, learn from the result).
        # False = this deployment has already told us it rejects a custom value -
        # stop sending it and save a round-trip on every subsequent call.
        self._temperature_supported: Optional[bool] = None

    # Tasks whose callers (see agents/atlas.py, tools/status_tools.py) do
    # `json.loads(response["content"])` and therefore need strict JSON output.
    _JSON_TASKS = ("methodology_selection", "complexity_scoring")

    async def chat(
        self, system_prompt: str, messages: list[dict[str, str]],
        tools: Optional[list[dict[str, Any]]] = None, temperature: float = 0.2,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = dict(
            model=self.settings.azure_openai_deployment_name,
            messages=[{"role": "system", "content": system_prompt}, *messages],
        )
        if self._temperature_supported is not False:
            kwargs["temperature"] = temperature
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        elif any(f"TASK: {task}" in system_prompt for task in self._JSON_TASKS):
            # Forces the model to emit parseable JSON (Azure OpenAI json_object mode)
            # instead of relying on prompt instructions alone.
            kwargs["response_format"] = {"type": "json_object"}

        try:
            resp = await self.client.chat.completions.create(**kwargs)
            if "temperature" in kwargs:
                self._temperature_supported = True
        except Exception as exc:
            # Some newer reasoning-family deployments (o-series, gpt-5-family)
            # only accept the default temperature and reject an explicit value.
            # Retry once without it, and remember that for every later call on
            # this client instance so we stop paying for the extra round-trip.
            if "temperature" in kwargs and "temperature" in str(exc).lower():
                logger.warning(f"Deployment rejected temperature={temperature}; retrying without it "
                               f"(will skip it on all future calls this session).")
                self._temperature_supported = False
                kwargs.pop("temperature", None)
                resp = await self.client.chat.completions.create(**kwargs)
            else:
                raise
        choice = resp.choices[0]
        return {
            "content": choice.message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                }
                for tc in (choice.message.tool_calls or [])
            ],
        }
