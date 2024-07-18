from typing import Dict, Any
from urllib.parse import urlencode

import aiohttp

from .core.config import ESIHubConfig
from .exceptions import ESIHubAuthenticationError


class ESIHubAuth:
    def __init__(self, client, config: ESIHubConfig):
        self.client = client
        self.config = config

    async def get_auth_url(self, scopes: str = None, state: str = None) -> str:
        params = {
            "response_type": "code",
            "redirect_uri": self.config.get("ESI_CALLBACK_URL"),
            "client_id": self.config.get("ESI_CLIENT_ID"),
        }
        if scopes:
            params["scope"] = scopes
        if state:
            params["state"] = state
        return f"https://login.eveonline.com/v2/oauth/authorize?{urlencode(params)}"

    async def get_access_token(self, code: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://login.eveonline.com/v2/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": self.config.get("ESI_CLIENT_ID"),
                    "client_secret": self.config.get("ESI_CLIENT_SECRET"),
                },
            ) as resp:
                if resp.status != 200:
                    raise ESIHubAuthenticationError(
                        f"Failed to get access token: {await resp.text()}"
                    )
                return await resp.json()

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://login.eveonline.com/v2/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.config.get("ESI_CLIENT_ID"),
                    "client_secret": self.config.get("ESI_CLIENT_SECRET"),
                },
            ) as resp:
                if resp.status != 200:
                    raise ESIHubAuthenticationError(
                        f"Failed to refresh token: {await resp.text()}"
                    )
                return await resp.json()
