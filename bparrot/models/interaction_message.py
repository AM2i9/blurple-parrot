import bparrot.http as http


class InteractionMessage:

    """
    Represents a Discord message object
    """

    #! Only a shell of a message object, needs more logic

    def __init__(self, _client, inter, data: dict):

        self._client = _client
        self._interaction = inter

        self.id: int = data["id"]
        self.channel_id: int = data["channel_id"]
        self.author = data["author"]
        self.content: str = data["content"]
        self.timestamp: str = data["timestamp"]
        self.edited_timestamp: str = data["edited_timestamp"]
        self.tts = data["tts"]
        self.mention_everyone = data["mention_everyone"]
        self.mentions: list = data["mentions"]
        self.mention_roles: list = data["mention_roles"]
        self.attachments: list = data["attachments"]
        self.embeds: list = data["embeds"]
        self.pinned: bool = data["pinned"]
        self.type: str = data["type"]

        self.guild_id = data.get("guild_id")
        self.member = data.get("member")
        self.mention_channels = data.get("mention_channels")
        self.reactions: list = data.get("reactions")
        self.nonce = data.get("nonce")
        self.webhook_id = data.get("webhook_id")
        self.activity = data.get("activity")
        self.application = data.get("application")
        self.application_id = data.get("application_id")
        self.message_reference = data.get("message_reference")
        self.thread = data.get("thread")
        self.components: list = data.get("components")
        self.sticker_items = data.get("sticker_items")
        self.stickers = data.get("stickers")

        self.interaction = data.get("interaction")

    async def edit(self, content: str = None):
        data = {}

        if content:
            data["content"] = content

        resp = await http.interaction_edit_followup(
            self._client.http_session, self._interaction, self.id, data
        )
        return InteractionMessage(self._client, self._interaction, resp)

    async def delete(self):
        await http.interaction_delete_followup(
            self._client.http_session, self._interaction, self.id
        )
