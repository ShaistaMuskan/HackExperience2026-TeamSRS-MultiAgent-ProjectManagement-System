"""
REAL Azure Key Vault client - centralized secret storage for all the above clients.
docs/architecture/azure-foundry-m365-integration-guide.md Section 5.

pip install azure-keyvault-secrets azure-identity
"""
from __future__ import annotations
from app.integrations.interfaces import SecretsClient
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("azure.keyvault")


class AzureKeyVaultClient(SecretsClient):
    def __init__(self) -> None:
        self.settings = get_settings()
        # TODO(integration-guide §5.2):
        #   from azure.identity import DefaultAzureCredential
        #   from azure.keyvault.secrets import SecretClient
        #   self.client = SecretClient(vault_url=self.settings.key_vault_url, credential=DefaultAzureCredential())
        self.client = None
        logger.warning("AzureKeyVaultClient instantiated without a live client. See integration guide Section 5.")

    def get_secret(self, name: str) -> str:
        # TODO: return self.client.get_secret(name).value
        raise NotImplementedError("Wire up Azure Key Vault call - see integration guide Section 5.2")
