import asyncio
from typing import Tuple

import bparrot.http as http


class InteractionHandler:
    def __init__(self, name: str, type_: int, handler):
        self.name = name
        self.type = type_
        self.handler = handler
        self._after_handler = None

    async def handle(self, inter) -> dict:
        args = inter.get_args()
        resp = await self.handler(inter, *args)
        if self._after_handler:
            asyncio.create_task(self._after_handler(inter, *args))
        return resp

    def after_response(self, func):
        self._after_handler = func
        return func


class SlashOption:
    def __init__(self, data: dict):
        self.name: str = data.get("name")
        self.type: int = data.get("type")

        self.value = data.get("value")

        self.options = data.get("options")
        if self.options is not None:
            self.options = list([SlashOption(o) for o in self.options])


class ApplicationCommand:
    def __init__(self, data: dict):

        self.id = data.get("id")
        self.type = data.get("type", 1)
        self.name = data.get("name")
        self.description = data.get("description")

        self.application_id = data.get("application_id")
        self.guild_id = data.get("guild_id")

        self.default_permission = data.get("default_permission", True)

        self.options = data.get("options", [])

        if self.options:
            self.options = list([SlashOption(o) for o in self.options])


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

    def get_args(self) -> Tuple:
        return tuple((o.value for o in self.data.options))

    def create_response(
        self,
        type_: int = 4,
        content: str = "",
    ):
        """
        Send a response to an interaction.
        """
        data = {}

        if content is not None:
            data["content"] = content

        resp = {"type": type_, "data": data}

        self._responded = True
        return resp

    async def followup(
        self,
        content: str = None,
    ):
        """
        Create a followup message to an interaction. Can only be used after
        the interaction has already been responded.
        """
        if not self._responded:
            raise Exception("Interaction has no initial response.")

        data = {}

        if content is not None:
            data["content"] = content

        await http.interaction_followup(self._client.http_session, self, data)

    async def delete_initial_response(self):
        """
        Delete the initial response to this interaction. Can only be used after
        the interaction has already been responded.
        """
        if not self._responded:
            raise Exception("Interaction has no initial response.")

        await http.interaction_delete_response(self._client.http_session, self)

    async def edit_initial_response(self, content: str = None):
        """
        Edit the initial response to this interaction. Can only be used after
        the interaction has already been responded.
        """
        if not self._responded:
            raise Exception("Interaction has no initial response.")

        data = {}

        if content is not None:
            data["content"] = content

        await http.interaction_edit_response(self._client.http_session, self, data)
