from typing import List
import logging
import asyncio
from asyncio.events import AbstractEventLoop

from aiohttp import web

from bparrot.http import HTTPClient
from bparrot.interaction import Interaction
from bparrot.core import *


_log = logging.getLogger("blurple-parrot")


class Client:
    def __init__(
        self,
        public_key: str = "",
        bot_token: str = "",
        interactions_path: str = "/",
        guild_ids: List[int] = [],
        loop: AbstractEventLoop = None,
    ):
        self.interaction_listeners = []

        self.interactions_path = interactions_path
        self.guild_ids = guild_ids

        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop

        if not bot_token and not public_key:
            raise Exception("A bot token or public key is required")

        self.http_client = HTTPClient(loop=loop, token=bot_token)

        self._public_key = public_key

        self.app = web.Application(loop=loop)

    def add_listener(self, listener):
        self.interaction_listeners.append(listener)

    def slash_command(
        self,
        name: str,
        description: str,
        options: List[SlashOption] = [],
        default_permission: bool = True,
        guild_id: int = None,
    ):
        """
        Create a SlashCommand Listener. Used as a decorator. Takes the same
        parameters as a SlashCommand object.
        """

        def _deco(func):
            _cmd = slash_command(
                name=name,
                description=description,
                options=options,
                default_permission=default_permission,
                guild_id=guild_id,
            )(func)
            self.add_listener(_cmd)
            return _cmd

        return _deco

    def user_command(self, name: str, guild_id: int = None):
        """
        Create a UserCommand Listener. Used as a decorator. Takes only the `name`
        parameter.
        """

        def _deco(func):
            _cmd = user_command(name, guild_id=guild_id)(func)
            self.add_listener(_cmd)
            return _cmd

        return _deco

    def message_command(self, name: str, guild_id: int = None):
        """
        Create a MessageCommand Listener. Used as a decorator. Takes only the `name`
        parameter.
        """

        def _deco(func):
            _cmd = message_command(name, guild_id=guild_id)(func)
            self.add_listener(_cmd)
            return _cmd

        return _deco

    def button(self, custom_id: str):
        """
        Create a ComponentIteraction Listener that is listening for a button of a
        certain `custom_id`.
        """

        def _deco(func):
            _cmp = button(custom_id)(func)
            self.add_listener(_cmp)
            return _cmp

        return _deco

    def select(self, custom_id: str):
        """
        Create a ComponentIteraction Listener that is listening for a SelectMenu of
        a certain `custom_id`.
        """

        def _deco(func):
            _cmp = select(custom_id)(func)
            self.add_listener(_cmp)
            return _cmp

        return _deco

    async def _register_commands(self):

        _global = []
        _guilds = {}

        for listener in self.interaction_listeners:
            if not listener.inter.guild_id:
                _global.append(listener.inter.to_dict())
            else:
                guild_id = str(listener.inter.guild_id)
                if guild_id not in _guilds:
                    _guilds[guild_id] = []
                _guilds[guild_id].append(listener.inter.to_dict())

        if self.guild_ids:
            for guild in self.guild_ids:
                await self.http_client.bulk_overwrite_guild_application_commands(
                    int(guild), _global
                )
        else:
            await self.http_client.bulk_overwrite_global_application_commands(_global)

        for guild_id, commands in _guilds.items():
            await self.http_client.bulk_overwrite_guild_application_commands(
                int(guild_id), commands
            )

    async def on_interaction(self, inter):
        for listener in self.interaction_listeners:
            if type(listener.inter) is type(inter.data):
                if listener.inter == inter.data:
                    return await listener.handle(inter)

    async def _handle_request(self, request: web.Request):

        body = await request.text()
        signature = request.headers.get("X-Signature-Ed25519")
        timestamp = request.headers.get("X-Signature-Timestamp")
        if not verify_key(self._public_key, body, signature, timestamp):
            return web.Response(status=401, text="Invalid Request Signature")

        _json = await request.json()

        if _json.get("type") == 1:
            return web.json_response({"type": 1})

        else:
            inter = Interaction(self, _json)
            resp = await self.on_interaction(inter) or {}
            return web.json_response(resp)

    async def close(self):
        await self.http_client.close()

    def _get_app(self) -> web.Application:
        self.app.router.add_post(self.interactions_path, self._handle_request)
        return self.app

    async def _pre_run(self):
        try:
            await self.http_client.login()
            if not self._public_key:
                self._public_key = self.http_client.get_public_key()
            await self._register_commands()
        except Exception as e:
            raise e

    def run(self, **kwargs):
        """
        Run the application locally. Simplest way to run the client, but
        does not use all CPU cores.

        https://docs.aiohttp.org/en/stable/deployment.html
        """

        try:
            self.loop.run_until_complete(self._pre_run())

            app = self._get_app()
            web.run_app(app, **kwargs)
        except Exception as e:
            raise e
        finally:
            asyncio.run(self.close())

    def run_factory(self):
        """
        Return a web.Application for running using another web server.
        """

        self.loop.run_until_complete(self._pre_run())
        app = self._get_app()
        return app
