import asyncio
from asyncio.events import AbstractEventLoop

import aiohttp
from aiohttp import web

from bparrot.verify import verify_key
from bparrot.interaction import Interaction, InteractionHandler


ACK_RESPONSE = {"type": 1}


class Client:
    def __init__(self, public_key: str, loop: AbstractEventLoop = None):
        self.interaction_handlers = []
        self.public_key = public_key

        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop

        self.app = web.Application(loop=loop)
        self.http_session = aiohttp.ClientSession(loop=loop)

    def command(self, name: str):
        def _deco(func):
            handler = InteractionHandler(name, 1, func)
            self.interaction_handlers.append(handler)
            return handler

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

    def run(self, interactions_route: str = "/", **kwargs):

        self.app.router.add_post(interactions_route, self._handle_request)

        web.run_app(self.app, **kwargs)
