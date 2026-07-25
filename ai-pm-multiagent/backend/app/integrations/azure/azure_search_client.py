"""
REAL Azure AI Search client (the RAG knowledge base retriever).

>>> WHERE THIS PLUGS IN <<<
docs/architecture/azure-foundry-m365-integration-guide.md
  - Section 4: Azure AI Search resource creation, index schema, vectorizer setup
  - Section 4.3: ingesting docs from app/knowledge_base/seed_docs (see
    backend/scripts/ingest_knowledge_base.py for the "push API" option)

Required env vars: AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_API_KEY, AZURE_SEARCH_INDEX_NAME
Optional: AZURE_OPENAI_EMBEDDING_DEPLOYMENT (enables vector/semantic search;
          without it this still works as keyword search against the index)

pip install azure-search-documents azure-identity
"""
from __future__ import annotations
from typing import Any, Optional

from app.integrations.interfaces import SearchClient
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("azure.search")


class AzureSearchClient(SearchClient):
    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.azure_search_endpoint or not self.settings.azure_search_api_key:
            logger.warning(
                "AzureSearchClient created with empty endpoint/key - search()/index_document() "
                "will fail. Set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY in .env "
                "(see integration guide Section 4)."
            )

        from azure.core.credentials import AzureKeyCredential
        from azure.search.documents.aio import SearchClient as SdkSearchClient

        self.client = SdkSearchClient(
            endpoint=self.settings.azure_search_endpoint,
            index_name=self.settings.azure_search_index_name,
            credential=AzureKeyCredential(self.settings.azure_search_api_key),
        )

        # Embeddings use the same Azure OpenAI resource as the chat model
        # (AzureFoundryLLMClient) but a distinct deployment - embedding models
        # are deployed independently in Foundry. Optional: with no
        # endpoint/key or no embedding deployment configured, index_document()
        # and search() silently skip the vector and fall back to keyword +
        # semantic search against `content` only.
        self._embedding_client = None
        if self.settings.azure_openai_endpoint and self.settings.azure_openai_api_key:
            from openai import AsyncAzureOpenAI

            self._embedding_client = AsyncAzureOpenAI(
                azure_endpoint=self.settings.azure_openai_endpoint,
                api_key=self.settings.azure_openai_api_key,
                api_version="2024-10-21",
            )

    async def _embed(self, text: str) -> Optional[list[float]]:
        """Best-effort: returns None (keyword-only) if no embedding deployment is configured."""
        if not self._embedding_client or not self.settings.azure_openai_embedding_deployment:
            return None
        try:
            resp = await self._embedding_client.embeddings.create(
                model=self.settings.azure_openai_embedding_deployment,
                input=text[:8000],  # stay well under the embedding model's token limit
            )
            return resp.data[0].embedding
        except Exception as exc:
            logger.warning(f"Embedding generation failed ({exc}); continuing with keyword-only indexing/search.")
            return None

    async def index_document(self, doc_id: str, content: str, metadata: dict[str, Any]) -> None:
        document: dict[str, Any] = {"id": doc_id, "content": content, **metadata}
        vector = await self._embed(content)
        if vector is not None:
            document["contentVector"] = vector

        result = await self.client.upload_documents(documents=[document])
        if not result[0].succeeded:
            raise RuntimeError(f"Azure AI Search indexing failed for '{doc_id}': {result[0].error_message}")
        logger.info(f"[AZURE SEARCH] indexed document {doc_id} ({metadata.get('category', 'n/a')})")

    async def search(self, query: str, top_k: int = 5, filters: Optional[str] = None) -> list[dict[str, Any]]:
        # rag_tools.retrieve_rag_documents() passes a plain category string
        # (e.g. "methodology") as `filters` - translate to an OData filter here
        # so callers don't need to know the index's filter syntax.
        odata_filter = f"category eq '{filters}'" if filters else None

        search_kwargs: dict[str, Any] = dict(
            search_text=query,
            top=top_k,
            filter=odata_filter,
            select=["id", "content", "category", "source", "filename"],
        )
        vector = await self._embed(query)
        if vector is not None:
            from azure.search.documents.models import VectorizedQuery

            search_kwargs["vector_queries"] = [
                VectorizedQuery(vector=vector, k_nearest_neighbors=top_k, fields="contentVector")
            ]

        try:
            results = await self.client.search(
                **search_kwargs, query_type="semantic", semantic_configuration_name="default",
            )
            scored = [r async for r in results]
        except Exception as exc:
            # Semantic ranking needs the "default" semantic configuration to
            # exist on the index (integration guide Section 4.2). If it hasn't
            # been set up yet, fall back to plain keyword/vector search rather
            # than hard-failing every RAG lookup Atlas makes.
            logger.warning(f"Semantic search failed ({exc}); retrying without semantic ranking.")
            results = await self.client.search(**search_kwargs)
            scored = [r async for r in results]

        out: list[dict[str, Any]] = []
        for r in scored:
            score = r.get("@search.reranker_score") or r.get("@search.score") or 0.0
            out.append({
                "id": r["id"],
                "content": r.get("content", ""),
                "metadata": {k: v for k, v in r.items() if k not in ("id", "content") and not k.startswith("@search")},
                "score": round(float(score), 4),
            })
        logger.info(f"[AZURE SEARCH] query='{query}' -> {[d['id'] for d in out]}")
        return out
