"""
In-memory RAG substitute for Azure AI Search.
Loads the seed knowledge base (app/knowledge_base/seed_docs/*) into memory and
performs simple TF-IDF-ish keyword scoring - just enough signal for Atlas to
retrieve the right methodology guide / template deterministically in a demo.

Swap for app/integrations/azure/azure_search_client.py (real vector + keyword
hybrid search against an Azure AI Search index) per the integration guide.
"""
from __future__ import annotations
import math
import re
from collections import Counter
from typing import Any, Optional

from app.integrations.interfaces import SearchClient
from app.core.logging import get_logger
from app.knowledge_base.loader import load_seed_docs

logger = get_logger("mock.search")


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class MockSearchClient(SearchClient):
    def __init__(self) -> None:
        self._index: dict[str, dict[str, Any]] = {}
        self._load_seed_docs()

    def _load_seed_docs(self) -> None:
        for d in load_seed_docs():
            self._index[d["id"]] = {
                "id": d["id"], "content": d["content"], "metadata": d["metadata"],
                "tokens": Counter(_tokenize(d["content"])),
            }
        logger.info(f"[MOCK SEARCH] loaded {len(self._index)} seed knowledge base documents")

    async def index_document(self, doc_id: str, content: str, metadata: dict[str, Any]) -> None:
        self._index[doc_id] = {
            "id": doc_id, "content": content, "metadata": metadata, "tokens": Counter(_tokenize(content)),
        }
        logger.info(f"[MOCK SEARCH] indexed document {doc_id} ({metadata.get('category', 'n/a')})")

    async def search(self, query: str, top_k: int = 5, filters: Optional[str] = None) -> list[dict[str, Any]]:
        query_tokens = _tokenize(query)
        scored: list[tuple[float, dict[str, Any]]] = []
        for doc in self._index.values():
            if filters and filters not in doc["metadata"].get("category", ""):
                continue
            score = sum(doc["tokens"].get(tok, 0) for tok in query_tokens)
            score = score / (1 + math.log(1 + sum(doc["tokens"].values())))
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [
            {"id": d["id"], "content": d["content"], "metadata": d["metadata"], "score": round(s, 4)}
            for s, d in scored[:top_k]
        ]
        logger.info(f"[MOCK SEARCH] query='{query}' -> {[r['id'] for r in results]}")
        return results
