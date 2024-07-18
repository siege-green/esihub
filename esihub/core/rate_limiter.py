import asyncio
import time
from typing import Dict

from multidict import CIMultiDictProxy

from .config import ESIHubConfig
from .logger import esihub_logger


class ESIHubRateLimiter:
    def __init__(self, config: ESIHubConfig):
        self.config = config
        self.limiters: Dict[str, Dict] = {}
        self.global_limit = self.config.get("ESI_RATE_LIMIT", 150)
        self.global_remaining = self.global_limit
        self.global_reset = 0
        self.lock = asyncio.Lock()

    async def acquire(self, endpoint: str):
        async with self.lock:
            await self._check_global_limit()

            if endpoint not in self.limiters:
                self.limiters[endpoint] = {
                    "limit": self.global_limit,
                    "remaining": self.global_limit,
                    "reset": 0,
                }

            limiter = self.limiters[endpoint]
            current_time = time.time()

            if current_time > limiter["reset"]:
                limiter["remaining"] = limiter["limit"]
                limiter["reset"] = current_time + 1  # Reset every second

            if limiter["remaining"] <= 0:
                wait_time = limiter["reset"] - current_time
                esihub_logger.debug(
                    "Rate limit reached, waiting",
                    extra={"endpoint": endpoint, "wait_time": wait_time},
                )
                await asyncio.sleep(wait_time)
                limiter["remaining"] = limiter["limit"]
                limiter["reset"] = time.time() + 1

            limiter["remaining"] -= 1
            self.global_remaining -= 1

    async def _check_global_limit(self):
        current_time = time.time()
        if current_time > self.global_reset:
            self.global_remaining = self.global_limit
            self.global_reset = current_time + 1

        if self.global_remaining <= 0:
            wait_time = self.global_reset - current_time
            esihub_logger.debug(
                "Global rate limit reached, waiting", extra={"wait_time": wait_time}
            )
            await asyncio.sleep(wait_time)
            self.global_remaining = self.global_limit
            self.global_reset = time.time() + 1

    def update_limit(self, endpoint: str, headers: CIMultiDictProxy[str]):
        if (
            "X-Esi-Error-Limit-Remain" in headers
            and "X-Esi-Error-Limit-Reset" in headers
        ):
            remain = int(headers["X-Esi-Error-Limit-Remain"])
            reset = int(headers["X-Esi-Error-Limit-Reset"])

            if endpoint in self.limiters:
                self.limiters[endpoint]["remaining"] = remain
                self.limiters[endpoint]["reset"] = time.time() + reset
            else:
                self.limiters[endpoint] = {
                    "limit": self.global_limit,
                    "remaining": remain,
                    "reset": time.time() + reset,
                }

        if "X-Esi-Error-Limit-Remain" in headers:
            self.global_remaining = int(headers["X-Esi-Error-Limit-Remain"])
        if "X-Esi-Error-Limit-Reset" in headers:
            self.global_reset = time.time() + int(headers["X-Esi-Error-Limit-Reset"])

        esihub_logger.debug(
            "Rate limit updated",
            extra={
                "endpoint": endpoint,
                "remaining": self.global_remaining,
                "reset": self.global_reset,
            },
        )
