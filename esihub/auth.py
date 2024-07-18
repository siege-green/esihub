from typing import Dict, Any
from urllib.parse import urlencode

import aiohttp

from .core.config import ESIHubConfig
from .exceptions import ESIHubAuthenticationError


class ESIHubAuth:
    def __init__(self, config: ESIHubConfig):
        self.config = config

        self.auth_base_url = "https://login.eveonline.com"
        self.token_url = f"{self.auth_base_url}/v2/oauth/token"
        self.authorize_url = f"{self.auth_base_url}/v2/oauth/authorize"
        self.verify_url = f"{self.auth_base_url}/oauth/verify"

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
        return f"{self.authorize_url}?{urlencode(params)}"

    async def get_token_verify(self, token: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.verify_url,
                headers={"Authorization": f"Bearer {token}"},
            ) as resp:
                if resp.status != 200:
                    raise ESIHubAuthenticationError(
                        f"Failed to verify token: {await resp.text()}"
                    )
                return await resp.json()

    async def get_access_token(self, code: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.token_url,
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
                self.token_url,
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
