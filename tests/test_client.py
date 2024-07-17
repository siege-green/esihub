from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from esihub import ESIHubClient
from esihub.exceptions import (ESIAuthenticationError, ESIHubException,
                               ESIRateLimitExceeded, ESIServerError)


class MockResponse:
    def __init__(self, data, status=200):
        self.data = data
        self.status = status

    async def json(self):
        return self.data

    async def text(self):
        return str(self.data)


class AsyncContextManagerMock:
    def __init__(self, return_value):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc, tb):
        pass


class MockClientSession:
    def __init__(self):
        self.closed = False
        self.request = AsyncMock()
        self.post = AsyncMock()
        self.get = AsyncMock()

    def _create_response(self, data, status=200):
        response = MockResponse(data, status)
        return AsyncContextManagerMock(response)

    async def close(self):
        self.closed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()


@pytest.fixture
def mock_session():
    return MockClientSession()


@pytest.fixture
async def mock_client(mock_session):
    with patch("aiohttp.ClientSession", return_value=mock_session):
        client = ESIHubClient()
        await client.initialize(fake=True)
        yield client
        await client.close()


@pytest.mark.asyncio
async def test_client_initialization(mock_client):
    assert mock_client.base_url == "https://esi.evetech.net"


# @pytest.mark.asyncio
# async def test_get_authorize_url(mock_client):
#     url = mock_client.get_authorize_url()
#     assert "https://login.eveonline.com/v2/oauth/authorize" in url
#     assert "client_id=test" in url
#     assert "redirect_uri=http://localhost" in url
#

# @pytest.mark.asyncio
# async def test_get_access_token(mock_client, mock_session):
#     mock_response = {"access_token": "test_token", "refresh_token": "refresh_token"}
#     mock_session.post.return_value = mock_session._create_response(mock_response)
#
#     token = await mock_client.get_access_token("test_code")
#     assert token["access_token"] == "test_token"
#     assert token["refresh_token"] == "refresh_token"
#
#
# @pytest.mark.asyncio
# async def test_refresh_token(mock_client, mock_session):
#     mock_response = {"access_token": "new_token", "refresh_token": "new_refresh_token"}
#     mock_session.post.return_value = mock_session._create_response(mock_response)
#
#     token = await mock_client.refresh_token("old_refresh_token")
#     assert token["access_token"] == "new_token"
#     assert token["refresh_token"] == "new_refresh_token"
#
#
# @pytest.mark.asyncio
# async def test_request(mock_client, mock_session):
#     mock_response = {"id": 123, "name": "Test Character"}
#     mock_session.request.return_value = mock_session._create_response(mock_response)
#
#     with patch.object(mock_client.cache, 'get', new_callable=AsyncMock, return_value=None), \
#             patch.object(mock_client.cache, 'set', new_callable=AsyncMock):
#         data = await mock_client.request("GET", "/characters/123/")
#         assert data == {"id": 123, "name": "Test Character"}
#
#
# @pytest.mark.asyncio
# async def test_caching(mock_client, mock_session):
#     mock_response = {"id": 123, "name": "Test Character"}
#     mock_session.request.return_value = mock_session._create_response(mock_response)
#
#     with patch.object(mock_client.cache, 'get', new_callable=AsyncMock, side_effect=[None, mock_response]), \
#             patch.object(mock_client.cache, 'set', new_callable=AsyncMock):
#         # First request should hit the API and cache the result
#         data1 = await mock_client.request("GET", "/characters/123/")
#         # Second request should hit the cache
#         data2 = await mock_client.request("GET", "/characters/123/")
#         assert data1 == data2
#         assert mock_session.request.call_count == 1
#
#
# @pytest.mark.asyncio
# async def test_rate_limiting(mock_client, mock_session):
#     mock_response = {"id": 123, "name": "Test Character"}
#     mock_session.request.return_value = mock_session._create_response(mock_response)
#
#     with patch.object(mock_client.rate_limiter, 'wait', new_callable=AsyncMock) as mock_wait:
#         await mock_client.request("GET", "/characters/123/")
#         mock_wait.assert_called_once()
#
#
# @pytest.mark.asyncio
# async def test_event_system(mock_client, mock_session):
#     events = []
#     mock_response = {"id": 123, "name": "Test Character"}
#     mock_session.request.return_value = mock_session._create_response(mock_response)
#
#     @mock_client.event_system.on('before_request')
#     async def on_before_request(**kwargs):
#         events.append(('before_request', kwargs))
#
#     @mock_client.event_system.on('after_request')
#     async def on_after_request(**kwargs):
#         events.append(('after_request', kwargs))
#
#     await mock_client.request("GET", "/characters/123/")
#
#     assert len(events) == 2
#     assert events[0][0] == 'before_request'
#     assert events[1][0] == 'after_request'
#
#
# @pytest.mark.asyncio
# async def test_dynamic_endpoint_generation(mock_client, mock_session):
#     mock_response = {"id": 123, "name": "Test Character"}
#     mock_session.request.return_value = mock_session._create_response(mock_response)
#
#     result = await mock_client.get_characters_character_id(character_id=123)
#
#     mock_session.request.assert_called_once_with(
#         "GET",
#         f"{mock_client.base_url}/characters/123/",
#         character_id=123
#     )
#     assert result == {"id": 123, "name": "Test Character"}
#
#
# @pytest.mark.asyncio
# async def test_error_handling(mock_client, mock_session):
#     mock_session.request.return_value = mock_session._create_response("Internal Server Error", status=500)
#
#     with pytest.raises(ESIServerError):
#         await mock_client.request("GET", "/characters/123/")
#
#
# @pytest.mark.asyncio
# async def test_authentication_error(mock_client, mock_session):
#     mock_session.request.return_value = mock_session._create_response("Forbidden", status=403)
#
#     with pytest.raises(ESIAuthenticationError):
#         await mock_client.request("GET", "/characters/123/")
#
#
# @pytest.mark.asyncio
# async def test_rate_limit_error(mock_client, mock_session):
#     mock_session.request.return_value = mock_session._create_response("Too Many Requests", status=429)
#
#     with pytest.raises(ESIRateLimitExceeded):
#         await mock_client.request("GET", "/characters/123/")
