import asyncio
import time

from ..core.logger import get_logger


class ESIRateLimiter:
    def __init__(self, rate: int = 150, per: float = 1.0):
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.monotonic()
        self.logger = get_logger(__name__)

    async def wait(self) -> None:
        now = time.monotonic()
        time_passed = now - self.last_check
        self.last_check = now
        self.allowance += time_passed * (self.rate / self.per)
        if self.allowance > self.rate:
            self.allowance = self.rate
        if self.allowance < 1:
            delay = (1 - self.allowance) * (self.per / self.rate)
            self.logger.debug(f"Rate limit reached. Waiting for {delay:.2f} seconds")
            await asyncio.sleep(delay)
            self.allowance = 0
        else:
            self.allowance -= 1
