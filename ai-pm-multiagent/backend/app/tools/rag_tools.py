"""Tool: RAG retrieval against the Project Management knowledge base (Azure AI Search)."""
from __future__ import annotations
from app.core.config import get_search_client
from app.core.logging import get_logger

logger = get_logger("tools.rag")


async def retrieve_rag_documents(query: str, top_k: int = 5, category: str | None = None) -> list[dict]:
    """
    category examples: 'methodology', 'template', 'historical', 'risk_rules', 'sop'
    (matches the `seed_docs/{category}__*.md` naming convention).
    """
    client = get_search_client()
    return await client.search(query=query, top_k=top_k, filters=category)


async def index_document(doc_id: str, content: str, category: str, extra_metadata: dict | None = None) -> None:
    client = get_search_client()
    metadata = {"category": category, **(extra_metadata or {})}
    await client.index_document(doc_id, content, metadata)
