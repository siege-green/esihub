import asyncio
from typing import Any, Dict, Optional

import redis
from cachetools import TTLCache
from multidict import CIMultiDictProxy

from .config import ESIHubConfig
from .logger import esihub_logger
from ..models import ESIHubResponse


class ESIHubCachePolicy:
    def __init__(self, ttl: int, max_size: int):
        self.ttl = ttl
        self.max_size = max_size


class ESIHubCache:
    def __init__(self, config: ESIHubConfig):
        self.config = config
        self.memory_cache = TTLCache(maxsize=1000, ttl=300)
        self.redis: Optional[redis.Redis] = None
        self.lock = asyncio.Lock()
        self.cache_enabled = self.config.get("CACHE_ENABLED", True)
        self.policies: Dict[str, ESIHubCachePolicy] = {}

    async def initialize(self):
        if not self.cache_enabled:
            esihub_logger.info("Caching is disabled.")
            return

        redis_url = self.config.get("REDIS_URL")
        if redis_url:
            try:
                self.redis = await redis.from_url(redis_url)
                await self.redis.ping()
                esihub_logger.info("Redis cache initialized successfully.")
            except Exception as e:
                esihub_logger.error(f"Failed to initialize Redis cache: {str(e)}")
                self.redis = None
        else:
            esihub_logger.info("Redis URL not provided. Using memory cache only.")

    async def get(
        self, method: str, path: str, params: Dict[str, Any]
    ) -> Optional[ESIHubResponse]:
        if not self.cache_enabled:
            return None

        cache_key = self._generate_cache_key(method, path, params)

        # Check memory cache first
        if cache_key in self.memory_cache:
            esihub_logger.debug("Cache hit (memory)", extra={"cache_key": cache_key})
            return self.memory_cache[cache_key]

        # Check Redis cache
        if self.redis:
            data = await self.redis.get(cache_key)
            if data:
                esi_response = ESIHubResponse.model_validate_json(data)
                self.memory_cache[cache_key] = esi_response
                esihub_logger.debug("Cache hit (Redis)", extra={"cache_key": cache_key})
                return esi_response

        esihub_logger.debug("Cache miss", extra={"cache_key": cache_key})
        return None

    async def set(
        self,
        method: str,
        path: str,
        params: Dict[str, Any],
        response: ESIHubResponse,
        headers: CIMultiDictProxy[str],
    ):
        if not self.cache_enabled:
            return

        cache_key = self._generate_cache_key(method, path, params)
        policy = self.get_policy(path)
        expires_in = self._get_cache_expiry(headers, policy)

        async with self.lock:
            self.memory_cache[cache_key] = response
            if self.redis:
                await self.redis.setex(
                    cache_key, expires_in, response.model_dump_json()
                )

        esihub_logger.debug(
            "Cached", extra={"cache_key": cache_key, "expires_in": expires_in}
        )

    async def invalidate(self, pattern: str):
        if not self.cache_enabled:
            return

        if self.redis:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
                esihub_logger.debug(
                    "Invalidated Redis cache", extra={"pattern": pattern}
                )

        # Invalidate memory cache
        for key in list(self.memory_cache.keys()):
            if pattern in key:
                del self.memory_cache[key]
        esihub_logger.debug("Invalidated memory cache", extra={"pattern": pattern})

    def _generate_cache_key(
        self, method: str, path: str, params: Dict[str, Any]
    ) -> str:
        sorted_params = sorted(params.items())
        return f"{method}:{path}:{sorted_params}"

    def _get_cache_expiry(
        self, headers: CIMultiDictProxy[str], policy: ESIHubCachePolicy
    ) -> int:
        if "Expires" in headers:
            from email.utils import parsedate
            import time

            expires = parsedate(headers["Expires"])
            if expires:
                return max(0, int(time.mktime(expires) - time.time()))
        return (
            policy.ttl
            if policy
            else int(headers.get("Cache-Control", "300").split("=")[-1])
        )

    async def close(self):
        if self.redis:
            await self.redis.close()
            esihub_logger.info("Redis connection closed.")

    def set_policy(self, path: str, policy: ESIHubCachePolicy):
        self.policies[path] = policy

    def get_policy(self, path: str) -> Optional[ESIHubCachePolicy]:
        return self.policies.get(path)
