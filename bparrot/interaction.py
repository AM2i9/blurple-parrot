import asyncio
from bparrot.application_commands import (
    MessageCommand,
    UserCommand,
    get_application_command,
    SlashCommand,
)
from typing import Iterable, List, Tuple

from bparrot.http import Req
from bparrot.components import ActionRow, ComponentInteraction, ComponentType
from bparrot.models import InteractionMessage, Embed, AllowedMentions


class InteractionListener:
    def __init__(self, interaction, handler):
        self.inter = interaction
        self.handler = handler

        self._after_response = None

    async def handle(self, inter) -> dict:

        args = []
        kwargs = {}

        if isinstance(inter.data, SlashCommand):
            kwargs = inter.get_args()
        elif isinstance(inter.data, UserCommand):
            args = [inter.data.member]
        elif isinstance(inter.data, MessageCommand):
            args = [inter.data.resolved_message]
        elif (
            isinstance(inter.data, ComponentInteraction)
            and inter.data.component_type == ComponentType.SELECT_MENU
        ):
            args = [inter.data.values]

        resp = await self.handler(inter, *args, **kwargs)
        if self._after_response:
            asyncio.create_task(self._after_response(inter, *args, **kwargs))
        return resp

    def after_response(self, func):
        self._after_response = func
        return func


class Interaction:
    def __init__(self, client, data: dict):
        self._client = client

        self.id: int = data.get("id")
        self.application_id: int = data.get("application_id")
        self.type: int = data.get("type")
        self.token: str = data.get("token")
        self.version: int = data.get("version")

        if self.type == 2:
            self.data = get_application_command(data.get("data"))
        elif self.type == 3:
            self.data = ComponentInteraction.from_dict(data.get("data"))

        self.guild_id: int = data.get("guild_id")
        self.author = data.get("member")

        self.channel_id = data.get("channel_id")

        self._responded = False

    def get_args(self) -> Tuple:
        return {o.name: o.value for o in self.data.options}

    def create_response(
        self,
        content: str = None,
        *,
        type_: int = 4,
        tts: bool = False,
        embed: Embed = None,
        embeds: List[Embed] = None,
        allowed_mentions: AllowedMentions = None,
        ephemeral: bool = False,
        components: list = [],
    ):
        """
        Send a response to an interaction.
        """
        data = {}

        if content:
            data["content"] = content

        if embeds and embed:
            raise Exception(
                "Can only use one of 'embed' or 'embeds' parameters at once."
            )

        if embed:
            _emb = embed.to_dict()
            if not _emb:
                raise Exception("Cannot send empty embed.")
            data["embeds"] = [_emb]
        elif embeds:
            data["embeds"] = []
            for e in embeds:
                if not isinstance(e, Embed):
                    raise Exception("Cannot send non-embed objects as Embeds.")
                _emb = e.to_dict()
                if not _emb:
                    raise Exception("Cannot send empty embed.")
                data["embeds"].append(_emb)

        if (type_ not in (1, 5, 6)) and not data:
            raise Exception("Cannot send empty response.")

        if tts:
            data["tts"] = bool(tts)

        if ephemeral:
            data["flags"] = 64

        if components:

            data["components"] = []

            for component in components:
                if isinstance(component, Iterable):
                    row = ActionRow(component)
                elif isinstance(component, ActionRow):
                    row = component
                else:
                    raise Exception(
                        "Components must be ActionRows or iterables of components"
                    )

                data["components"].append(row.to_dict())

        if allowed_mentions:
            data["allowed_mentions"] = allowed_mentions.to_dict()

        resp = {"type": type_, "data": data}
        print(resp)

        self._responded = True
        return resp

    def ack(self):
        """
        Acknowledge the interaction, and show a "thinking" message. The
        interaction must be edited later to display content.
        """
        return self.create_response(type_=1)

    think = ack

    async def followup(
        self,
        content: str = None,
        *,
        tts: bool = False,
        embeds: list = None,
        allowed_mentions: list = None,
        ephemeral: bool = False,
        components: list = None,
    ):
        """
        Create a followup message to an interaction. Can only be used after
        the interaction has already been responded.
        """
        if not self._responded:
            raise Exception("Cannot send followup message before intial response.")

        data = self.create_response(
            content=content,
            tts=tts,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            ephemeral=ephemeral,
            components=components,
        )["data"]

        req = Req("POST", f"/webhooks/{self.application_id}/{self.token}", json=data)
        resp = await self._client.http_client.request(req)
        resp_message = InteractionMessage(self._client, self, resp)
        return resp_message

    async def delete_initial_response(self):
        """
        Delete the initial response to this interaction. Can only be used after
        the interaction has already been responded.
        """
        if not self._responded:
            raise Exception("Interaction has no initial response.")

        req = Req(
            "DELETE", f"/webhooks{self.application_id}/{self.token}/messages/@original"
        )
        await self._client.http_client.request(req)

    async def edit_initial_response(
        self,
        content: str = "",
        *,
        tts: bool = False,
        embeds: list = None,
        allowed_mentions: list = None,
        ephemeral: bool = False,
        components: list = None,
    ):
        """
        Edit the initial response to this interaction. Can only be used after
        the interaction has already been responded.
        """
        if not self._responded:
            raise Exception("Interaction has no initial response.")

        data = self.create_response(
            content=content,
            tts=tts,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            ephemeral=ephemeral,
            components=components,
        )["data"]

        req = Req(
            "PATCH",
            f"/webhooks/{self.application_id}/{self.token}/messages/@original",
            json=data,
        )
        resp = await self._client.http_client.request(req)
        resp_message = InteractionMessage(self._client, self, resp)
        return resp_message
