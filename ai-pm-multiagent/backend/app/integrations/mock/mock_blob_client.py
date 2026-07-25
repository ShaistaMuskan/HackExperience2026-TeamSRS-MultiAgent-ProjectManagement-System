from __future__ import annotations
from app.integrations.interfaces import BlobStorageClient
from app.core.logging import get_logger

logger = get_logger("mock.blob")


class MockBlobStorageClient(BlobStorageClient):
    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}

    async def upload_file(self, container: str, blob_name: str, content_bytes: bytes) -> str:
        key = f"{container}/{blob_name}"
        self.store[key] = content_bytes
        url = f"https://mockstorage.blob.core.windows.net/{key}"
        logger.info(f"[MOCK BLOB] uploaded {key} ({len(content_bytes)} bytes)")
        return url

    async def download_file(self, container: str, blob_name: str) -> bytes:
        key = f"{container}/{blob_name}"
        if key not in self.store:
            raise FileNotFoundError(key)
        return self.store[key]
