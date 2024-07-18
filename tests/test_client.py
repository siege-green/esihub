from unittest.mock import MagicMock, patch

import pytest

from esihub import ESIHubClient, ESIHubResponse
from esihub.core.config import ESIHubConfig


@pytest.fixture
def esihub_config():
    config = ESIHubConfig()
    config.update(
        {
            "ESI_CLIENT_ID": "test_client_id",
            "ESI_CLIENT_SECRET": "test_client_secret",
            "ESI_CALLBACK_URL": "https://test.com/callback",
            "ESI_BASE_URL": "https://esi.evetech.net",
            "USE_HTTPS": True,
            "MAX_CONCURRENT_REQUESTS": 10,
            "DRY_RUN": True,
        }
    )
    return config


@pytest.fixture
async def esihub_client(esihub_config):
    client = ESIHubClient(esihub_config)
    await client.initialize()
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_client_initialization(esihub_config):
    client = ESIHubClient(esihub_config)
    assert client.base_url == "https://esi.evetech.net"
    assert client.semaphore._value == 10


@pytest.mark.asyncio
async def test_request_success(esihub_client):
    with patch.object(esihub_client.session, "request") as mock_request:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json.return_value = {"data": "test"}
        mock_request.return_value.__aenter__.return_value = mock_response

        response = await esihub_client.request("GET", "/test/", data="test")

        assert response.status == 200
        assert response.data == {"data": "test"}

@pytest.mark.asyncio
async def test_batch_request(esihub_client):
    with patch.object(esihub_client, "_make_request") as mock_make_request:
        mock_make_request.side_effect = [
            ESIHubResponse(status=200, headers={}, data="test1"),
            ESIHubResponse(status=200, headers={}, data="test2"),
            ESIHubResponse(status=200, headers={}, data="test3"),
        ]

        requests = [
            {"method": "GET", "path": "/test1/", "data": "test1"},
            {"method": "GET", "path": "/test2/", "data": "test2"},
            {"method": "GET", "path": "/test3/", "data": "test3"},
        ]

        responses = await esihub_client.batch_request(requests)

        assert len(responses) == 3
        assert responses[0].data == {"data": "test1"}
        assert responses[1].data == {"data": "test2"}
        assert responses[2].data == {"data": "test3"}


@pytest.mark.asyncio
async def test_paginated_request(esihub_client):
    with patch.object(esihub_client, "request") as mock_request:
        mock_request.side_effect = [
            ESIHubResponse(status=200, headers={"X-Pages": "3"}, data={"page": 1}),
            ESIHubResponse(status=200, headers={"X-Pages": "3"}, data={"page": 2}),
            ESIHubResponse(status=200, headers={"X-Pages": "3"}, data={"page": 3}),
        ]

        pages = []
        async for page in esihub_client.paginated_request("GET", "/test/"):
            pages.append(page)

        assert len(pages) == 3
        assert pages == [{"page": 1}, {"page": 2}, {"page": 3}]
