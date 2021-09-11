import sys
import asyncio
import logging
from asyncio.events import AbstractEventLoop
from typing import Optional

import aiohttp
from aiohttp import ClientSession

import bparrot

API_ENDPOINT = "https://discord.com/api/v9"

_log = logging.getLogger(__name__)

class NotAuthorized(Exception):
    pass


class LoginFailure(Exception):
    pass


class EndpointNotFound(Exception):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def __str__(self):
        return f"Discord Endpoint {self.endpoint} not found."



class Req:
    def __init__(self, method: str, path: str, **params):
        self.method = method
        self.path = path
        self.params = params
        self.url = API_ENDPOINT + path


class HTTPClient:
    def __init__(
        self, token: Optional[str] = None, loop: Optional[AbstractEventLoop] = None
    ):
        self.loop = loop or asyncio.get_event_loop()
        self._session = ClientSession(loop=self.loop)

        user_agent = "DiscordBot (https://github.com/AM2i9/blurple-parrot {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent: str = user_agent.format(
            bparrot.__version__, sys.version_info, aiohttp.__version__
        )

        self.token = token
        if not self.token:
            _log.warn("Token required for non-interaction response API calls.")
        else:
            self._application = loop.run_until_complete(self.login())
            self.application_id = self._application["id"]


    async def request(self, req: Req):

        headers = req.params.get("headers", {})
        if self.token:
            headers["Authorization"] = f"Bot {self.token}"
        req.params["headers"] = headers

        async with self._session.request(req.method, req.url, **req.params) as resp:

            if resp.status == 204:
                return None
            elif resp.status == 404:
                raise EndpointNotFound(req.path)
            elif resp.status == 401:
                raise NotAuthorized(await resp.text())
            elif resp.status == 400:
                raise Exception(f"Bad request: {await resp.json()}")

            return await resp.json()

    async def close(self):
        await self._session.close()
    
    async def login(self):
        
        try:
            _data = await self.request(Req("GET", "/oauth2/applications/@me"))
        except NotAuthorized as e:
            raise LoginFailure("Invalid Token") from e
        
        return _data

    def get_public_key(self):
        return self._application["verify_key"]