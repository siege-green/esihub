import json
from typing import Any, Optional

import fakeredis
import redis.asyncio as redis

from ..core.config import esi_config
from ..core.logger import get_logger


class ESICache:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or esi_config.get("ESI_REDIS_URL")
        self.logger = get_logger(__name__)
        self.redis: Optional[redis.Redis] = None

    async def initialize(self, fake=False):
        if self.redis_url and not fake:
            self.redis = await redis.from_url(self.redis_url, decode_responses=True)
        elif self.redis_url == "fakeredis" or fake:
            self.redis = await fakeredis.FakeAsyncRedis(decode_responses=True)
        await self.redis.ping()

    async def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            await self.initialize()
        value = await self.redis.get(key)
        if value:
            self.logger.debug(f"Cache hit for key: {key}")
            return json.loads(value)
        self.logger.debug(f"Cache miss for key: {key}")
        return None

    async def set(self, key: str, value: Any, expire: int = 300) -> None:
        if not self.redis:
            await self.initialize()
        await self.redis.set(key, json.dumps(value), ex=expire)
        self.logger.debug(f"Set cache for key: {key}, expires in {expire} seconds")

    async def delete(self, key: str) -> None:
        if not self.redis:
            await self.initialize()
        await self.redis.delete(key)
        self.logger.debug(f"Deleted cache for key: {key}")

    async def close(self) -> None:
        if self.redis:
            await self.redis.aclose()  # DeprecationWarning 해결을 위해 aclose() 사용
        self.logger.info("Closed Redis connection")
