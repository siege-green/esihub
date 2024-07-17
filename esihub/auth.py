from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .client import ESIHubClient

import asyncio


class ESITokenManager:
    def __init__(self, client: "ESIHubClient"):
        self.client = client
        self.tokens: Dict[int, Dict[str, Any]] = {}
        self.refresh_lock = asyncio.Lock()

    async def get_token(self, character_id: int) -> Optional[str]:
        if character_id in self.tokens:
            token_info = self.tokens[character_id]
            if datetime.now() >= token_info["expires_at"] - timedelta(minutes=5):
                async with self.refresh_lock:
                    if datetime.now() >= token_info["expires_at"] - timedelta(
                        minutes=5
                    ):
                        new_tokens = await self.client.refresh_token(
                            token_info["refresh_token"]
                        )
                        self.update_tokens(character_id, new_tokens)
            return self.tokens[character_id]["access_token"]
        return None

    def update_tokens(self, character_id: int, tokens: Dict[str, Any]) -> None:
        self.tokens[character_id] = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_at": datetime.now() + timedelta(seconds=tokens["expires_in"]),
        }

    def remove_tokens(self, character_id: int) -> None:
        if character_id in self.tokens:
            del self.tokens[character_id]
