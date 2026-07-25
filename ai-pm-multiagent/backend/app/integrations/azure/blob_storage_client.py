"""
REAL Azure Blob Storage client - ingestion point for project briefs / documents.
docs/architecture/azure-foundry-m365-integration-guide.md Section 1 (storage account + containers).

pip install azure-storage-blob azure-identity
"""
from __future__ import annotations
from app.integrations.interfaces import BlobStorageClient
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("azure.blob")


class AzureBlobStorageClient(BlobStorageClient):
    """
    Uses DefaultAzureCredential, which - with no Entra ID app registration
    required yet (that's Section 2) - picks up your `az login` session locally.
    Requires the "Storage Blob Data Contributor" role assigned to your own
    user on the storage account (integration guide Section 1, Step 5).
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.azure_storage_account_url:
            logger.warning(
                "AzureBlobStorageClient created with no AZURE_STORAGE_ACCOUNT_URL - "
                "upload_file()/download_file() will fail. See integration guide Section 1."
            )
        from azure.storage.blob.aio import BlobServiceClient
        from azure.identity.aio import DefaultAzureCredential

        self.credential = DefaultAzureCredential()
        self.service_client = BlobServiceClient(
            account_url=self.settings.azure_storage_account_url,
            credential=self.credential,
        )

    async def upload_file(self, container: str, blob_name: str, content_bytes: bytes) -> str:
        container_client = self.service_client.get_container_client(container)
        await container_client.upload_blob(name=blob_name, data=content_bytes, overwrite=True)
        logger.info(f"Uploaded blob '{blob_name}' ({len(content_bytes)} bytes) to container '{container}'")
        return container_client.get_blob_client(blob_name).url

    async def download_file(self, container: str, blob_name: str) -> bytes:
        stream = await self.service_client.get_blob_client(container, blob_name).download_blob()
        return await stream.readall()
