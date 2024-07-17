import fakeredis.aioredis
import pytest

from esihub import ESIHubClient
from esihub.core.cache import ESICache


@pytest.fixture
async def fake_redis():
    server = await fakeredis.FakeAsyncRedis()
    yield server
    await server.flushall()
    await server.aclose()


@pytest.fixture
async def esi_cache(fake_redis):
    cache = ESICache(redis_url="fakeredis")
    cache.redis = fake_redis
    await cache.initialize(fake=True)
    return cache


@pytest.fixture
async def client(esi_cache):
    client = ESIHubClient(
        client_id="test",
        client_secret="test",
        callback_url="http://localhost",
        redis_url="fakeredis",
    )
    client.cache = esi_cache
    await client.initialize(fake=True)
    yield client
    await client.close()
