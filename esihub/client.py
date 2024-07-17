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
from .exceptions import ESIAuthenticationError, ESIHubException
from .models import ESIRequestParams
from .utils import load_swagger_spec


class ESIHubClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        callback_url: str,
        base_url: str = "https://esi.evetech.net",
        redis_url: Optional[str] = None,
    ):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url
        self.cache = ESICache(redis_url)
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
        await self.cache.initialize(fake=fake)
        generate_endpoints(self)

    async def close(self):
        if self.session:
            await self.connection_pool.release(self.session)
        await self.cache.close()

    async def request(
        self, method: str, path: str, token: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        params = ESIRequestParams(
            method=method, path=path, character_id=kwargs.get("character_id")
        )
        await self.event_system.emit("before_request", params=params, kwargs=kwargs)

        if token:
            kwargs["headers"] = kwargs.get("headers", {})
            kwargs["headers"]["Authorization"] = f"Bearer {token}"

        url = f"{self.base_url}{path}"
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
                await self.cache.set(cache_key, data)
                await self.event_system.emit(
                    "after_request", params=params, response=data
                )
                return data
        except aiohttp.ClientError as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise ESIHubException(f"Request failed: {str(e)}")

    async def batch_request(
        self, requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return await asyncio.gather(
            *(self.request(**req) for req in requests), return_exceptions=True
        )

    def get_authorize_url(
        self, scopes: Optional[str] = None, state: Optional[str] = None
    ) -> str:
        params = {
            "response_type": "code",
            "redirect_uri": self.callback_url,
            "client_id": self.client_id,
        }
        if scopes:
            params["scope"] = scopes
        if state:
            params["state"] = state
        return f"https://login.eveonline.com/v2/oauth/authorize?{'&'.join(f'{k}={v}' for k, v in params.items())}"

    async def get_access_token(self, code: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://login.eveonline.com/v2/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                },
                auth=aiohttp.BasicAuth(self.client_id, self.client_secret),
            ) as resp:
                if resp.status != 200:
                    raise ESIAuthenticationError("Failed to obtain access token")
                return await resp.json()

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://login.eveonline.com/v2/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                auth=aiohttp.BasicAuth(self.client_id, self.client_secret),
            ) as resp:
                if resp.status != 200:
                    raise ESIAuthenticationError("Failed to refresh token")
                return await resp.json()

    async def revoke_token(self, token: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://login.eveonline.com/v2/oauth/revoke",
                data={
                    "token": token,
                },
                auth=aiohttp.BasicAuth(self.client_id, self.client_secret),
            ) as resp:
                if resp.status != 200:
                    raise ESIAuthenticationError("Failed to revoke token")

    async def get_token_info(self, token: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://login.eveonline.com/oauth/verify",
                headers={"Authorization": f"Bearer {token}"},
            ) as resp:
                if resp.status != 200:
                    raise ESIAuthenticationError("Failed to get token info")
                return await resp.json()

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
