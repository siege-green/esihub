import pytest
from esihub import ESIHubClient
from esihub.exceptions import (
    ESIHubException,
    ESIServerError,
    ESIAuthenticationError,
    ESIRateLimitExceeded,
)
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_client_initialization():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )
    assert client.base_url == "https://esi.evetech.net"


@pytest.mark.asyncio
async def test_get_authorize_url():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )
    url = await client.get_authorize_url()
    assert "https://login.eveonline.com/v2/oauth/authorize" in url
    assert "client_id=test" in url
    assert "redirect_uri=http://localhost" in url


@pytest.mark.asyncio
async def test_get_access_token():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "access_token": "test_token",
        "refresh_token": "refresh_token",
    }

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        token = await client.get_access_token("test_code")
        assert token["access_token"] == "test_token"
        assert token["refresh_token"] == "refresh_token"


@pytest.mark.asyncio
async def test_refresh_token():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "access_token": "new_token",
        "refresh_token": "new_refresh_token",
    }

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        token = await client.refresh_token("old_refresh_token")
        assert token["access_token"] == "new_token"
        assert token["refresh_token"] == "new_refresh_token"


@pytest.mark.asyncio
async def test_request():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"id": 123, "name": "Test Character"}

    with patch("aiohttp.ClientSession.request", return_value=mock_response):
        data = await client.request(method="GET", path="/characters/123/")
        assert data["id"] == 123
        assert data["name"] == "Test Character"


@pytest.mark.asyncio
async def test_batch_request():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )

    mock_response1 = AsyncMock()
    mock_response1.status = 200
    mock_response1.json.return_value = {"id": 123, "name": "Character 1"}

    mock_response2 = AsyncMock()
    mock_response2.status = 200
    mock_response2.json.return_value = {"id": 456, "name": "Character 2"}

    with patch(
        "aiohttp.ClientSession.request", side_effect=[mock_response1, mock_response2]
    ):
        results = await client.batch_request(
            [
                {"method": "GET", "path": "/characters/123/"},
                {"method": "GET", "path": "/characters/456/"},
            ]
        )

        assert len(results) == 2
        assert results[0]["id"] == 123
        assert results[0]["name"] == "Character 1"
        assert results[1]["id"] == 456
        assert results[1]["name"] == "Character 2"


@pytest.mark.asyncio
async def test_event_system():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )

    events = []

    @client.event_system.on("before_request")
    def on_before_request(**kwargs):
        events.append(("before_request", kwargs))

    @client.event_system.on("after_request")
    def on_after_request(**kwargs):
        events.append(("after_request", kwargs))

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"id": 123, "name": "Test Character"}

    with patch("aiohttp.ClientSession.request", return_value=mock_response):
        await client.request(method="GET", path="/characters/123/")

    assert len(events) == 2
    assert events[0][0] == "before_request"
    assert events[1][0] == "after_request"
    assert events[0][1]["params"].method == "GET"
    assert events[0][1]["params"].path == "/characters/123/"
    assert events[1][1]["response"]["id"] == 123
    assert events[1][1]["response"]["name"] == "Test Character"


@pytest.mark.asyncio
async def test_rate_limiting():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"id": 123, "name": "Test Character"}

    with patch(
        "aiohttp.ClientSession.request", return_value=mock_response
    ) as mock_request:
        with patch("esihub.core.rate_limiter.ESIRateLimiter.wait") as mock_wait:
            await client.request(method="GET", path="/characters/123/")
            mock_wait.assert_called_once()


@pytest.mark.asyncio
async def test_caching():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"id": 123, "name": "Test Character"}

    with patch(
        "aiohttp.ClientSession.request", return_value=mock_response
    ) as mock_request:
        with patch(
            "esihub.core.cache.ESICache.get", return_value=None
        ) as mock_cache_get:
            with patch("esihub.core.cache.ESICache.set") as mock_cache_set:
                # First request should hit the API and cache the result
                data1 = await client.request(method="GET", path="/characters/123/")
                mock_request.assert_called_once()
                mock_cache_set.assert_called_once()

                # Reset mocks
                mock_request.reset_mock()
                mock_cache_get.return_value = {"id": 123, "name": "Test Character"}

                # Second request should hit the cache
                data2 = await client.request(method="GET", path="/characters/123/")
                mock_request.assert_not_called()
                assert data1 == data2


@pytest.mark.asyncio
async def test_error_handling():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )

    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.text.return_value = "Internal Server Error"

    with patch("aiohttp.ClientSession.request", return_value=mock_response):
        with pytest.raises(ESIServerError):
            await client.request(method="GET", path="/characters/123/")


@pytest.mark.asyncio
async def test_authentication_error():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )

    mock_response = AsyncMock()
    mock_response.status = 403
    mock_response.text.return_value = "Forbidden"

    with patch("aiohttp.ClientSession.request", return_value=mock_response):
        with pytest.raises(ESIAuthenticationError):
            await client.request(method="GET", path="/characters/123/")


@pytest.mark.asyncio
async def test_rate_limit_error():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )

    mock_response = AsyncMock()
    mock_response.status = 429
    mock_response.text.return_value = "Too Many Requests"

    with patch("aiohttp.ClientSession.request", return_value=mock_response):
        with pytest.raises(ESIRateLimitExceeded):
            await client.request(method="GET", path="/characters/123/")


@pytest.mark.asyncio
async def test_dynamic_endpoint_generation():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"id": 123, "name": "Test Character"}

    with patch(
        "aiohttp.ClientSession.request", return_value=mock_response
    ) as mock_request:
        # Assuming 'get_characters_character_id' is a dynamically generated endpoint
        result = await client.get_characters_character_id(character_id=123)

        mock_request.assert_called_once_with(
            "GET",
            "https://esi.evetech.net/latest/characters/123/",
            headers={},
            params=None,
        )
        assert result == {"id": 123, "name": "Test Character"}


@pytest.mark.asyncio
async def test_connection_pool():
    client = ESIHubClient(
        client_id="test", client_secret="test", callback_url="http://localhost"
    )

    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"id": 123, "name": "Test Character"}
    mock_session.request.return_value = mock_response

    with patch(
        "esihub.core.connection_pool.ESIConnectionPool.get", return_value=mock_session
    ):
        await client.request(method="GET", path="/characters/123/")
        await client.request(method="GET", path="/characters/456/")

        assert mock_session.request.call_count == 2


if __name__ == "__main__":
    pytest.main()
