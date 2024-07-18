import asyncio
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Callable,
    Awaitable,
    AsyncIterator,
)

import aiohttp
from aiohttp import ClientSession, TCPConnector
from pydantic import BaseModel, ValidationError

from esihub.api.endpoints import generate_endpoints
from esihub.auth import ESIHubAuth
from esihub.core.async_profiler import ESIHubAsyncProfiler, profile
from esihub.core.background_tasks import ESIHubBackgroundTaskManager
from esihub.core.cache import ESIHubCache
from esihub.core.config import ESIHubConfig, esi_config
from esihub.core.dry_run import ESIHubDryRunMode
from esihub.core.error_handler import ESIHubErrorHandler
from esihub.core.event_system import ESIHubEventSystem
from esihub.core.logger import configure_logging, esihub_logger
from esihub.core.metrics import ESIHubMetrics
from esihub.core.rate_limiter import ESIHubRateLimiter
from esihub.exceptions import ESIHubValidationError, ESIHubError
from esihub.models import ESIHubResponse, ESIHubRequestParams
from esihub.utils import (
    validate_url,
    retry_with_exponential_backoff,
    validate_input,
    load_swagger_spec,
)

T = TypeVar("T", bound="ESIHubClient")


class ESIHubClient:
    def __init__(
        self,
        config: ESIHubConfig = esi_config,
        auth: Optional[ESIHubAuth] = None,
        cache: Optional[ESIHubCache] = None,
        rate_limiter: Optional[ESIHubRateLimiter] = None,
        error_handler: Optional[ESIHubErrorHandler] = None,
        event_system: Optional[ESIHubEventSystem] = None,
    ) -> None:
        self.config = config
        self.base_url = self.config.get("ESI_BASE_URL")
        if not validate_url(self.base_url):
            raise ValueError("Invalid base URL")
        if self.config.get("USE_HTTPS") and not self.base_url.startswith("https://"):
            raise ValueError("HTTPS is required")

        self.auth = auth or ESIHubAuth(config)
        self.cache = cache or ESIHubCache(config)
        self.rate_limiter = rate_limiter or ESIHubRateLimiter(config)
        self.error_handler = error_handler or ESIHubErrorHandler()
        self.event_system = event_system or ESIHubEventSystem()
        self.session: Optional[ClientSession] = None
        self.semaphore = asyncio.Semaphore(
            self.config.get("MAX_CONCURRENT_REQUESTS", 100)
        )

        self.background_tasks = ESIHubBackgroundTaskManager()
        self.metrics = ESIHubMetrics()
        self.dry_run_mode = ESIHubDryRunMode(self)

        self.profiler = ESIHubAsyncProfiler()

        self.swagger_spec = load_swagger_spec()

        configure_logging(config)
        generate_endpoints(self)

    async def __aenter__(self: T) -> T:
        await self.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        await self.close()

    async def initialize(self) -> None:
        ssl_context = self._create_ssl_context()
        connector = TCPConnector(
            limit=self.config.get("MAX_CONNECTIONS", 100), ssl=ssl_context
        )
        self.session = ClientSession(
            connector=connector,
            headers={"User-Agent": self.config.get("ESI_USER_AGENT")},
        )
        await self.cache.initialize()
        await self.background_tasks.start()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
        await self.cache.close()
        await self.background_tasks.stop()

    @retry_with_exponential_backoff()
    @profile
    async def request(
        self,
        method: str,
        path: str,
        model: Optional[Type[BaseModel]] = None,
        **kwargs: Any,
    ) -> ESIHubResponse:
        if not validate_input(path, r"^/[\w\-/{}]+$"):
            raise ValueError("Invalid path")

        if self.config.get("DRY_RUN"):
            return await self.dry_run_mode.request(method, path, **kwargs)

        async with self.semaphore:
            with self.metrics.measure_request_duration(method, path):
                self.metrics.increment_request(method, path)
                try:
                    response = await self._make_request(method, path, **kwargs)
                    if model:
                        try:
                            validated_data = model(**response.data)
                            response.data = validated_data.model_dump()
                        except ValidationError as e:
                            raise ESIHubValidationError(
                                f"Response validation failed: {e}"
                            )
                    return response
                except Exception as e:
                    self.metrics.increment_error(type(e).__name__)
                    raise

    async def _make_request(
        self, method: str, path: str, **kwargs: Any
    ) -> ESIHubResponse:
        if not self.session:
            await self.initialize()

        url = f"{self.base_url}/latest{path}"
        await self.rate_limiter.acquire(path)

        try:
            cached_response = await self.cache.get(method, path, kwargs)
            if cached_response:
                return cached_response

            params = ESIHubRequestParams(method=method, path=path, **kwargs)
            await self.event_system.emit("before_request", params=params)

            esihub_logger.info("Making request", extra={"method": method, "path": path})

            async with self.session.request(method, url, **kwargs) as response:
                response_data = await response.json()

                self.rate_limiter.update_limit(path, response.headers)

                if response.status >= 400:
                    await self.error_handler.handle_error(
                        response.status, response_data
                    )

                esi_response = ESIHubResponse(
                    status=response.status,
                    headers=dict(response.headers),
                    data=response_data,
                )

                await self.cache.set(
                    method, path, kwargs, esi_response, response.headers
                )

                esihub_logger.info(
                    "Received response", extra={"status": response.status}
                )
                await self.event_system.emit(
                    "after_request", params=params, response=esi_response
                )

                return esi_response
        except aiohttp.ClientError as e:
            esihub_logger.error("Request failed", extra={"error": str(e)})
            raise ESIHubError(f"Request failed: {str(e)}")

    async def batch_request(self, requests: List[Dict[str, Any]]) -> tuple[Any]:
        async def bounded_request(req: Dict[str, Any]) -> ESIHubResponse:
            return await self.request(**req)

        return await asyncio.gather(*(bounded_request(req) for req in requests))

    async def stream_request(
        self, method: str, path: str, **kwargs: Any
    ) -> AsyncIterator[Any]:
        if not self.session:
            await self.initialize()

        url = f"{self.base_url}{path}"
        await self.rate_limiter.acquire(path)

        async with self.session.request(method, url, **kwargs) as response:
            async for chunk in response.content.iter_any():
                yield chunk

    async def bulk_operation(
        self, operation: str, items: List[Any], batch_size: int = 100
    ) -> List[Any]:
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            batch_results = await getattr(self, operation)(batch)
            results.extend(batch_results)
        return results

    def _create_ssl_context(self):
        import ssl

        ssl_context = ssl.create_default_context()
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        return ssl_context

    async def paginated_request(
        self, method: str, path: str, **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        page = 1
        while True:
            kwargs["params"] = kwargs.get("params", {})
            kwargs["params"]["page"] = page
            response = await self.request(method, path, **kwargs)
            yield response.data
            if "X-Pages" in response.headers and page < int(
                response.headers["X-Pages"]
            ):
                page += 1
            else:
                break

    async def add_background_task(
        self, coroutine: Callable[..., Awaitable[Any]], *args, **kwargs
    ) -> None:
        await self.background_tasks.add_task(coroutine, *args, **kwargs)

    def __getattr__(self, name: str):
        if (
            name.startswith("get_")
            or name.startswith("post_")
            or name.startswith("put_")
            or name.startswith("delete_")
        ):
            method, *path_parts = name.split("_")
            path = "/" + "/".join(path_parts) + "/"

            async def dynamic_endpoint(**kwargs):
                return await self.request(method.upper(), path, **kwargs)

            return dynamic_endpoint
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )
