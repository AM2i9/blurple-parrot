from typing import List
import logging
import asyncio
from asyncio.events import AbstractEventLoop

from aiohttp import web
from nacl.signing import VerifyKey

from bparrot.http import HTTPClient
from bparrot.interaction import Interaction, InteractionListener
from bparrot.components import ComponentInteraction, ComponentType
from bparrot.application_commands import (
    MessageCommand,
    SlashCommand,
    SlashOption,
    UserCommand,
)


ACK_RESPONSE = {"type": 1}

_log = logging.getLogger("blurple-parrot")


def verify_key(pk: str, body: bytes, signature: str, timestamp: str) -> bool:
    """
    Validate the following headers of an interaction request:
        - X-Signature-Ed25519
        - X-Signature-Timestamp

    https://discord.com/developers/docs/interactions/receiving-and-responding#security-and-authorization
    """

    key = VerifyKey(bytes.fromhex(pk))

    try:
        key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
        return True
    except Exception as e:
        _log.warn(e)
    return False


def slash_command(
    name: str,
    description: str,
    options: List[SlashOption] = [],
    default_permission: bool = True,
):
    return SlashCommand(
        name=name,
        description=description,
        options=options,
        default_permission=default_permission,
    )


def user_command(name: str):
    return UserCommand(name)


def message_command(name: str):
    return MessageCommand(name)


def button_click(custom_id: str):
    return ComponentInteraction(
        custom_id=custom_id,
        component_type=ComponentType.BUTTON
    )


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

    def add_listener(self, inter, func):
        _listener = InteractionListener(inter, func)
        self.interaction_listeners.append(_listener)
        return _listener

    def slash_command(self, **kwargs):
        def _deco(func):
            _intr = slash_command(**kwargs)
            _listener = self.add_listener(_intr, func)
            return _listener

        return _deco

    def user_command(self, name: str):
        def _deco(func):
            _intr = user_command(name)
            _listener = self.add_listener(_intr, func)
            return _listener

        return _deco

    def message_command(self, name: str):
        def _deco(func):
            _intr = message_command(name)
            _listener = self.add_listener(_intr, func)
            return _listener

        return _deco

    def button_click(self, custom_id: str):
        def _deco(func):
            _intr = button_click(custom_id)
            _listener = self.add_listener(_intr, func)
            return _listener

        return _deco
        
    async def process_interaction(self, inter):
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
            resp = await self.process_interaction(inter) or {}
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
