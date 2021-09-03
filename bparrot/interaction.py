import asyncio

import bparrot.http as http


class InteractionHandler:
    def __init__(self, name: str, type_: int, handler):
        self.name = name
        self.type = type_
        self.handler = handler
        self._after_handler = None

    async def handle(self, inter) -> dict:
        resp = await self.handler(inter)
        if self._after_handler:
            asyncio.create_task(self._after_handler(inter))
        return resp

    def after_response(self, func):
        self._after_handler = func
        return func


class ApplicationCommand:
    def __init__(self, data: dict):

        self.id = data.get("id")
        self.type = data.get("type", 1)
        self.name = data.get("name")
        self.description = data.get("description")

        self.application_id = data.get("application_id")
        self.guild_id = data.get("guild_id")

        self.options = data.get("options", [])
        self.default_permission = data.get("default_permission", True)


class Interaction:
    def __init__(self, client, data: dict):
        self._client = client

        self.id: int = data.get("id")
        self.application_id: int = data.get("application_id")
        self.type: int = data.get("type")
        self.token: str = data.get("token")
        self.version: int = data.get("version")

        if self.type == 2:
            self.data = ApplicationCommand(data.get("data"))

        self.guild_id: int = data.get("guild_id")
        self.author = data.get("member")

        self.channel_id = data.get("channel_id")

        self._responded = False

    def create_response(
        self,
        type_: int = 4,
        content: str = "",
    ):
        data = {}

        if content is not None:
            data["content"] = content

        resp = {"type": type_, "data": data}

        self._responded = True
        return resp
    
    async def followup(
        self,
        type_: int = 4,
        content: str = "",
    ):
        if not self._responded:
            raise Exception("Interaction has no initial response.")

        data = {}

        if content is not None:
            data["content"] = content

        await http.interaction_followup(self._client.http_session, self, data)

