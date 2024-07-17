from typing import Any, Callable

from ..core.logger import get_logger
from ..exceptions import (ESIAuthenticationError, ESIHubException,
                          ESIRateLimitExceeded, ESIServerError)


class ESIErrorHandler:
    def __init__(self):
        self.logger = get_logger(__name__)

    async def handle_http_error(self, status_code: int, response_text: str) -> None:
        if 400 <= status_code < 500:
            if status_code == 429:
                raise ESIRateLimitExceeded(f"Rate limit exceeded: {response_text}")
            elif status_code == 403:
                raise ESIAuthenticationError(f"Authentication failed: {response_text}")
            else:
                raise ESIHubException(f"Client error: {status_code} - {response_text}")
        elif status_code >= 500:
            raise ESIServerError(f"Server error: {status_code} - {response_text}")

    async def retry_with_backoff(
        self, func: Callable[..., Any], max_retries: int = 3, base_delay: float = 1
    ) -> Any:
        import asyncio

        retries = 0
        while retries < max_retries:
            try:
                return await func()
            except ESIHubException as e:
                retries += 1
                if retries == max_retries:
                    raise
                delay = base_delay * (2 ** (retries - 1))
                self.logger.warning(
                    f"Retry {retries}/{max_retries} after {delay} seconds. Error: {str(e)}"
                )
                await asyncio.sleep(delay)
