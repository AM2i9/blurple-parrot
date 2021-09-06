import logging
import asyncio
from asyncio.events import AbstractEventLoop

from aiohttp import web
from nacl.signing import VerifyKey

from bparrot.http import HTTPClient
from bparrot.interaction import Interaction, InteractionHandler


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


class Client:
    def __init__(
        self,
        application_id: str,
        public_key: str,
        bot_token: str = "",
        interactions_path: str = "/",
        loop: AbstractEventLoop = None,
    ):
        self.interaction_handlers = []

        self.application_id = application_id
        self.public_key = public_key
        self.bot_token = bot_token

        self.interactions_path = interactions_path

        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop

        self.app = web.Application(loop=loop)
        self.http_client = HTTPClient(loop=loop, token=bot_token)

    def add_command(self, func, type, name: str):
        handler = InteractionHandler(name, type, func)
        self.interaction_handlers.append(handler)
        return handler

    def slash_command(self, name: str):
        def _deco(func):
            return self.add_command(func, 1, name)

        return _deco

    def user_command(self, name: str):
        def _deco(func):
            return self.add_command(func, 2, name)

        return _deco

    def message_command(self, name: str):
        def _deco(func):
            return self.add_command(func, 3, name)

        return _deco

    async def process_interaction(self, inter):
        for handler in self.interaction_handlers:
            if handler.type == inter.data.type and handler.name == inter.data.name:
                return await handler.handle(inter)

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
