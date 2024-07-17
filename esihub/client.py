from __future__ import annotations

import asyncio
from types import TracebackType
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientSession

from .api.endpoints import generate_endpoints
from .auth import ESITokenManager
from .core.cache import ESICache
from .core.connection_pool import ESIConnectionPool
from .core.error_handler import ESIErrorHandler
from .core.event_system import ESIEventSystem
from .core.logger import get_logger
from .core.rate_limiter import ESIRateLimiter
from .exceptions import ESIHubException
from .models import ESIRequestParams
from .utils import load_swagger_spec


class ESIHubClient:
    def __init__(
        self,
        base_url: str = "https://esi.evetech.net",
    ):
        self.base_url = base_url
        self.cache = ESICache()
        self.rate_limiter = ESIRateLimiter()
        self.connection_pool = ESIConnectionPool()
        self.error_handler = ESIErrorHandler()
        self.token_manager = ESITokenManager(self)
        self.event_system = ESIEventSystem()
        self.session: Optional[ClientSession] = None
        self.swagger_spec = load_swagger_spec()
        self.logger = get_logger(__name__)

    async def __aenter__(self) -> ESIHubClient:
        await self.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def initialize(self, fake: bool = False):
        self.session = await self.connection_pool.get()
        if self.cache.redis:
            await self.cache.initialize(fake=fake)
        generate_endpoints(self)

    async def close(self):
        if self.session:
            await self.connection_pool.release(self.session)
        if self.cache.redis:
            await self.cache.close()

    async def request(
        self, method: str, path: str, token: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        params = ESIRequestParams(
            method=method, path=path
        )
        await self.event_system.emit("before_request", params=params, kwargs=kwargs)

        if token:
            kwargs["headers"] = kwargs.get("headers", {})
            kwargs["headers"]["Authorization"] = f"Bearer {token}"

        url = f"{self.base_url}/latest{path}"
        if self.cache.redis:
            cache_key = f"{method}:{url}:{str(kwargs)}"
            cached_response = await self.cache.get(cache_key)
            if cached_response:
                self.logger.debug(f"Cache hit for {url}")
                return cached_response

        await self.rate_limiter.wait()

        try:
            assert self.session is not None
            async with self.session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    await self.error_handler.handle_http_error(
                        response.status, await response.text()
                    )
                data = await response.json()
                if self.cache.redis:
                    await self.cache.set(cache_key, data)
                await self.event_system.emit(
                    "after_request", params=params, response=data
                )
                return data
        except Exception as e:
            self.logger.error(f"Request url: {url}")
            self.logger.error(f"Request failed: {str(e)}")
            raise ESIHubException(f"Request failed: {str(e)}")
        except aiohttp.ClientError as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise ESIHubException(f"Request failed: {str(e)}")

    async def batch_request(
        self, requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return await asyncio.gather(
            *(self.request(**req) for req in requests), return_exceptions=True
        )

    def __getattr__(self, name: str):
        if name.startswith("get_") or name.startswith("post_"):
            method, *path_parts = name.split("_")
            path = "/" + "/".join(path_parts) + "/"

            async def dynamic_endpoint(**kwargs):
                return await self.request(method.upper(), path, **kwargs)

            return dynamic_endpoint
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )
