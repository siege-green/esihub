from typing import Optional

import aiohttp

from ..core.logger import get_logger


class ESIConnectionPool:
    def __init__(self, pool_size: int = 100):
        self.pool_size = pool_size
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = get_logger(__name__)

    async def get(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=self.pool_size)
            )
            self.logger.info(
                f"Created new ClientSession with pool size {self.pool_size}"
            )
        return self.session

    async def release(self, session: aiohttp.ClientSession) -> None:
        if session and not session.closed:
            await session.close()
            self.logger.info("Closed ClientSession")

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.info("Closed ConnectionPool")
