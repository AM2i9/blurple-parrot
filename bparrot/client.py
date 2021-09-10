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
        application_id: str,
        public_key: str,
        bot_token: str = "",
        interactions_path: str = "/",
        loop: AbstractEventLoop = None,
    ):
        self.interaction_listeners = []

        self.application_id = application_id
        self.public_key = public_key
        self.bot_token = bot_token

        self.interactions_path = interactions_path

        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop

        self.app = web.Application(loop=loop)
        self.http_client = HTTPClient(loop=loop, token=bot_token)

    def add_listener(self, listener):
        self.interaction_listeners.append(listener)

    def slash_command(
        self,
        name: str,
        description: str,
        options: List[SlashOption] = [],
        default_permission: bool = True,
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
            )(func)
            self.add_listener(_cmd)
            return _cmd
        return _deco

    def user_command(self, name: str):
        """
        Create a UserCommand Listener. Used as a decorator. Takes only the `name`
        parameter.
        """
        def _deco(func):
            _cmd = user_command(name)(func)
            self.add_listener(_cmd)
            return _cmd
        return _deco

    def message_command(self, name: str):
        """
        Create a MessageCommand Listener. Used as a decorator. Takes only the `name`
        parameter.
        """

        def _deco(func):
            _cmd = message_command(name)(func)
            self.add_listener(_cmd)
            return _cmd
        return _deco

    def button(self, custom_id: str):
        """
        Create a ComponentIteraction Listener that is listening for a button of a
        certain `custom_id`.
        """

        def _deco(func):
            _cmp= button(custom_id)(func)
            self.add_listener(_cmp)
            return _cmp
        return _deco

    def select(self, custom_id: str):
        """
        Create a ComponentIteraction Listener that is listening for a SelectMenu of
        a certain `custom_id`.
        """

        def _deco(func):
            _cmp= select(custom_id)(func)
            self.add_listener(_cmp)
            return _cmp
        return _deco

    async def on_interaction(self, inter):
        for listener in self.interaction_listeners:
            if type(listener.inter) is type(inter.data):
                if listener.inter == inter.data:
                    return await listener.handle(inter)

    async def _handle_request(self, request: web.Request):

        body = await request.text()
        signature = request.headers.get("X-Signature-Ed25519")
        timestamp = request.headers.get("X-Signature-Timestamp")
        if not verify_key(self.public_key, body, signature, timestamp):
            return web.Response(status=401, text="Invalid Request Signature")

        _json = await request.json()

        if _json.get("type") == 1:
            return web.json_response(ACK_RESPONSE)

        else:
            inter = Interaction(self, _json)
            resp = await self.on_interaction(inter) or {}
            return web.json_response(resp)

    async def close(self):
        await self.http_client.close()

    def get_app(self) -> web.Application:
        """
        Get the web application for running using another web server.
        """
        self.app.router.add_post(self.interactions_path, self._handle_request)
        return self.app

    def run(self, **kwargs):
        """
        Run the application locally. Simplest way to run the client, but
        does not use all CPU cores.

        https://docs.aiohttp.org/en/stable/deployment.html
        """

        app = self.get_app()

        try:
            web.run_app(app, **kwargs)
        except Exception as e:
            raise e
        finally:
            asyncio.run(self.close())
