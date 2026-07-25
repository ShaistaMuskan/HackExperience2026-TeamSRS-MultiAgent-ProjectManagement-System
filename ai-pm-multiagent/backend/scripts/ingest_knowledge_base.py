"""
One-off script: pushes app/knowledge_base/seed_docs/* (.md and .docx) into
whichever SearchClient is currently active (mock or real Azure AI Search -
see core/config.py's USE_MOCK_SEARCH / USE_MOCK_INTEGRATIONS).

This is the "push API" ingestion option from the integration guide's
Section 4.3 (the alternative to pointing an Azure AI Search indexer at Blob
Storage via the Portal). Uses the same app/knowledge_base/loader.py that
MockSearchClient loads from automatically in mock mode - this script is what
makes the real index have the same content.

Usage (from backend/):
    python -m scripts.ingest_knowledge_base

Requires AZURE_SEARCH_ENDPOINT / AZURE_SEARCH_API_KEY / AZURE_SEARCH_INDEX_NAME
to be set in .env and USE_MOCK_SEARCH=false (or USE_MOCK_INTEGRATIONS=false)
for this to actually reach a real index - otherwise it just re-populates the
in-memory mock, which is harmless but pointless to run standalone.
"""
from __future__ import annotations
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings, get_integration_status  # noqa: E402
from app.tools import rag_tools  # noqa: E402
from app.knowledge_base.loader import load_seed_docs, SEED_DOCS_DIR  # noqa: E402


async def main() -> None:
    status = get_integration_status()["search"]["status"]
    settings = get_settings()
    print(f"Search integration is currently: {status.upper()}  (index={settings.azure_search_index_name})")
    if status == "mock":
        print("USE_MOCK_SEARCH (or USE_MOCK_INTEGRATIONS) is true - this will only "
              "repopulate the in-memory mock. Set USE_MOCK_SEARCH=false in .env to "
              "actually ingest into your real Azure AI Search index.\n")

    docs = load_seed_docs()
    if not docs:
        print(f"No .md or .docx files found in {SEED_DOCS_DIR}")
        return

    ok, failed = 0, []
    for d in docs:
        try:
            await rag_tools.index_document(
                doc_id=d["id"], content=d["content"], category=d["metadata"]["category"],
                extra_metadata={"source": d["metadata"]["source"], "filename": d["metadata"]["filename"]},
            )
            print(f"  ok   {d['id']}  ({d['metadata']['category']})")
            ok += 1
        except Exception as exc:
            print(f"  FAIL {d['id']}  -> {exc}")
            failed.append(d["id"])

    print(f"\nIndexed {ok}/{len(docs)} document(s).")
    if failed:
        print(f"Failed: {failed}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
