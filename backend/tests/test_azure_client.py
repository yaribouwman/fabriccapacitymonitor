import pytest
from app.services.azure_client import AzureClient


@pytest.mark.asyncio
async def test_azure_client_initialization():
    client = AzureClient()
    assert client.arm_endpoint == "https://management.azure.com"
    assert client.api_version == "2023-11-01"
    await client.close()
