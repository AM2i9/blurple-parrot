import sys
import asyncio
import logging
from asyncio.events import AbstractEventLoop
from typing import List, Optional

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
        self, token: Optional[str] = None, token_type: str = "Bot", loop: Optional[AbstractEventLoop] = None
    ):
        self.loop = loop or asyncio.get_event_loop()
        self._session = ClientSession(loop=self.loop)

        user_agent = "DiscordBot (https://github.com/AM2i9/blurple-parrot {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent: str = user_agent.format(
            bparrot.__version__, sys.version_info, aiohttp.__version__
        )

        self.token_type = token_type.title()
        self.token = token
        if not self.token:
            _log.warn("Token required for non-interaction response API calls.")

    async def request(self, req: Req):

        headers = req.params.get("headers", {})
        if self.token:
            headers["Authorization"] = f"{self.token_type} {self.token}"
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

        self._application = _data
        self.application_id = _data["id"]
        return _data

    async def get_global_application_commands(self) -> List[dict]:
        """
        Fetch all of the global commands for your application.
        """
        _req = Req("GET", f"/applications/{self.application_id}/commands")
        return await self.request(_req)

    async def create_global_application_command(self, cmd: dict):
        """
        Create a new global command. New global commands will be available in
        all guilds after 1 hour.
        """
        _req = Req("POST", f"/applications/{self.application_id}/commands", json=cmd)
        return await self.request(_req)

    async def get_global_application_command(self, cmd_id: int):
        """
        Fetch a global command for your application.
        """
        _req = Req("GET", f"/applications/{self.application_id}/commands/{cmd_id}")
        return await self.request(_req)

    async def edit_global_application_command(self, cmd_id: int, params: dict):
        """
        Edit a global command. Updates will be available in all guilds after 1
        hour.
        """
        _req = Req(
            "PATCH",
            f"/applications/{self.application_id}/commands/{cmd_id}",
            json=params,
        )
        return await self.request(_req)

    async def delete_global_application_command(self, cmd_id: int):
        """
        Deletes a global command.
        """
        _req = Req("DELETE", f"/applications/{self.application_id}/commands/{cmd_id}")
        return await self.request(_req)

    async def bulk_overwrite_global_application_commands(self, cmds: List[dict]):
        """
        Takes a list of application commands, overwriting the existing global
        command list for this application. Updates will be available in all
        guilds after 1 hour. Commands that do not already exist will count
        toward daily application command create limits.
        """
        _req = Req("PUT", f"/applications/{self.application_id}/commands", json=cmds)
        return await self.request(_req)

    async def get_guild_application_commands(self, guild_id: int):
        """
        Fetch all of the guild commands for your application for a specific
        guild.
        """
        _req = Req(
            "GET", f"/applications/{self.application_id}/guilds/{guild_id}/commands"
        )
        return await self.request(_req)

    async def create_guild_application_command(self, guild_id: int, cmd: dict):
        """
        Create a new guild command. New guild commands will be available in the
        guild immediately.
        """
        _req = Req(
            "POST", f"/applications/{self.application_id}/guilds/{guild_id}/commands"
        )
        return await self.request(_req)

    async def get_guild_application_command(self, guild_id: int, cmd_id: int):
        """
        Fetch a guild command for your application.
        """
        _req = Req(
            "GET",
            f"/applications/{self.application_id}/guilds/{guild_id}/commands/{cmd_id}",
        )
        return await self.request(_req)

    async def edit_guild_application_command(
        self, guild_id: int, cmd_id: int, params: dict
    ):
        """
        Edit a guild command. Updates for guild commands will be available
        immediately.
        """
        _req = Req(
            "PATCH",
            f"/applications/{self.application_id}/guilds/{guild_id}/commands/{cmd_id}",
            json=params,
        )
        return await self.request(_req)

    async def delete_guild_application_command(self, guild_id: int, cmd_id: int):
        """
        Delete a guild command.
        """
        _req = Req(
            "DELETE",
            f"/applications/{self.application_id}/guilds/{guild_id}/commands/{cmd_id}",
        )
        return await self.request(_req)

    async def bulk_overwrite_guild_application_commands(
        self, guild_id: int, cmds: List[dict]
    ):
        """
        Takes a list of application commands, overwriting the existing command
        list for this application for the targeted guild.
        """
        _req = Req(
            "PUT",
            f"/applications/{self.application_id}/guilds/{guild_id}/commands",
            json=cmds,
        )
        return await self.request(_req)

    def get_public_key(self):
        return self._application["verify_key"]
