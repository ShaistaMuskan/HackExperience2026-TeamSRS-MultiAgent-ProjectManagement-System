import os
from app.integrations.interfaces import SecretsClient
from app.core.logging import get_logger

logger = get_logger("mock.secrets")


class MockSecretsClient(SecretsClient):
    """Falls back to environment variables instead of Azure Key Vault."""

    def get_secret(self, name: str) -> str:
        value = os.getenv(name, f"mock-secret-{name}")
        logger.info(f"[MOCK KEY VAULT] resolved secret '{name}'")
        return value
