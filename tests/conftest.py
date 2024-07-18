import pytest

from esihub import ESIHubClient


@pytest.fixture
async def client():
    client = ESIHubClient()
    await client.initialize()
    yield client
    await client.close()
