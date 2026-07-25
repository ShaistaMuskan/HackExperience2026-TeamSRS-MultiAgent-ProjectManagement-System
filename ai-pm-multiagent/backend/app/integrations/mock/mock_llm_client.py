"""
Deterministic, rule-based stand-in for the Azure AI Foundry Agent Service /
Azure OpenAI reasoning backend.

This is the ONE piece of the system that is most valuable to replace early -
see docs/architecture/azure-foundry-m365-integration-guide.md Section 3 for
the exact steps to swap this for a real Foundry Agent (gpt-4o / gpt-4o-mini
deployment) via app/integrations/azure/azure_openai_client.py.

It implements just enough heuristic "reasoning" (keyword-based classification,
templated generation) so that Atlas and Sentinel produce believable,
deterministic output during local demos/tests without any API key.
"""
from __future__ import annotations
import json
import re
from typing import Any, Optional

from app.integrations.interfaces import LLMClient
from app.core.logging import get_logger

logger = get_logger("mock.llm")

AGILE_KEYWORDS = ["sprint", "agile", "iterative", "backlog", "mvp", "startup", "evolving requirements", "fast-moving"]
WATERFALL_KEYWORDS = ["fixed scope", "regulatory", "compliance", "contract", "sequential", "government", "audited"]
KANBAN_KEYWORDS = ["continuous", "support", "maintenance", "flow", "ticket", "helpdesk", "ongoing operations"]
PRINCE2_KEYWORDS = ["governance", "stage gate", "board", "prince2", "formal oversight", "public sector"]


class MockLLMClient(LLMClient):
    """
    `chat()` inspects the system_prompt's `task` marker (set by the calling
    agent, e.g. "methodology_selection", "wbs_generation", "status_report")
    and returns a structured, deterministic response shaped like what an
    Azure OpenAI / Foundry Agent chat-completion with tool-calling would return.
    """

    async def chat(
        self, system_prompt: str, messages: list[dict[str, str]],
        tools: Optional[list[dict[str, Any]]] = None, temperature: float = 0.2,
    ) -> dict[str, Any]:
        task = self._extract_task(system_prompt)
        user_content = "\n".join(m["content"] for m in messages if m["role"] == "user")

        if task == "methodology_selection":
            return {"content": json.dumps(self._select_methodology(user_content)), "tool_calls": []}
        if task == "complexity_scoring":
            return {"content": json.dumps(self._score_complexity(user_content)), "tool_calls": []}
        if task == "status_report":
            return {"content": self._status_report(user_content), "tool_calls": []}
        if task == "risk_narrative":
            return {"content": self._risk_narrative(user_content), "tool_calls": []}

        logger.warning(f"[MOCK LLM] unrecognized task marker, echoing input. system_prompt={system_prompt[:80]}")
        return {"content": f"[mock-llm no-op response for: {user_content[:200]}]", "tool_calls": []}

    @staticmethod
    def _extract_task(system_prompt: str) -> str:
        m = re.search(r"TASK:\s*(\w+)", system_prompt)
        return m.group(1) if m else ""

    @staticmethod
    def _select_methodology(text: str) -> dict[str, Any]:
        text_l = text.lower()
        scores = {
            "agile_scrum": sum(k in text_l for k in AGILE_KEYWORDS),
            "waterfall": sum(k in text_l for k in WATERFALL_KEYWORDS),
            "kanban": sum(k in text_l for k in KANBAN_KEYWORDS),
            "prince2": sum(k in text_l for k in PRINCE2_KEYWORDS),
        }
        if sum(scores.values()) == 0:
            return {
                "methodology": "hybrid",
                "rationale": "No strong signal for a single methodology was found in the brief; "
                              "recommending a hybrid approach (Waterfall phase gates + Agile sprint execution) "
                              "as a safe default that a human PM should confirm.",
                "confidence": 0.4,
            }
        top = max(scores, key=scores.get)
        if list(scores.values()).count(scores[top]) > 1:
            return {
                "methodology": "hybrid",
                "rationale": f"Multiple methodology signals detected ({scores}); recommending hybrid.",
                "confidence": 0.55,
            }
        return {
            "methodology": top,
            "rationale": f"Brief language most closely matches {top.replace('_', ' ').title()} "
                         f"(keyword signal score={scores[top]}).",
            "confidence": min(0.6 + 0.1 * scores[top], 0.95),
        }

    @staticmethod
    def _score_complexity(text: str) -> dict[str, Any]:
        word_count = len(text.split())
        integration_terms = ["integration", "third-party", "compliance", "multi-region", "regulatory", "legacy"]
        hits = sum(t in text.lower() for t in integration_terms)
        score = min(0.15 + 0.05 * hits + min(word_count / 4000, 0.3), 0.95)
        return {"complexity_score": round(score, 2), "signals": {"integration_terms_found": hits, "word_count": word_count}}

    @staticmethod
    def _status_report(context: str) -> str:
        return (
            "## Executive Status Summary\n\n"
            f"{context}\n\n"
            "_This narrative is templated by MockLLMClient. Replace with a real "
            "Azure AI Foundry Agent call for natural-language generation quality._"
        )

    @staticmethod
    def _risk_narrative(context: str) -> str:
        return f"Risk assessment: {context} _(templated by MockLLMClient)_"
