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


class Embed:
    """
    A Discord Embed object
    """
    def __init__(
        self,
        *,
        title: str = None,
        description: str = None,
        url: str = None,
        timestamp: str = None,
        color: str = None,
    ):
        self.title = title
        self.description = description
        self.url = url
        self.timestamp = timestamp
        self.color = color

        self.fields = []

        self.video = None
        self.author = None
        self.footer = None
        self.image = None
        self.provider = None
        self.thumbnail = None

    def set_footer(
        self, text: str = None, *, icon_url: str = None, proxy_url: str = None
    ):
        self.footer = {"text": text, "icon_url": icon_url, "proxy_url": proxy_url}

    def set_image(
        self,
        *,
        url: str = None,
        height: int = None,
        width: int = None,
        proxy_url: str = None,
    ):
        self.image = {}

        if url:
            self.image["url"] = url
        if height:
            self.image["height"] = height
        if width:
            self.image["width"] = width
        if proxy_url:
            self.image["proxy_url"] = proxy_url

    def set_thumbnail(
        self,
        *,
        url: str = None,
        height: int = None,
        width: int = None,
        proxy_url: str = None,
    ):
        self.thumbnail = {}

        if url:
            self.thumbnail["url"] = url
        if height:
            self.thumbnail["height"] = height
        if width:
            self.thumbnail["width"] = width
        if proxy_url:
            self.thumbnail["proxy_url"] = proxy_url

    def set_video(
        self,
        *,
        url: str = None,
        height: int = None,
        width: int = None,
        proxy_url: str = None,
    ):
        self.video = {}

        if url:
            self.video["url"] = url
        if height:
            self.video["height"] = height
        if width:
            self.video["width"] = width
        if proxy_url:
            self.video["proxy_url"] = proxy_url

    def set_author(
        self,
        *,
        name: str = None,
        url: str = None,
        icon_url: str = None,
        proxy_icon_url: str = None,
    ):
        self.author = {}

        if name:
            self.author["name"] = name
        if url:
            self.author["url"] = url
        if icon_url:
            self.author["icon_url"] = icon_url
        if proxy_icon_url:
            self.author["proxy_icon_url"] = proxy_icon_url

    def set_provider(
        self,
        *,
        name: str = None,
        url: str = None,
    ):
        self.provider = {}

        if name:
            self.provider["name"] = name
        if url:
            self.provider["url"] = url

    def add_field(self, *, name: str = None, value: str = None, inline: bool = False):
        self.fields.append({"name": name, "value": value, "inline": inline})

    def remove_field(self, index: int):
        del self.fields[index]

    def to_dict(self):

        _emb = {}

        if self.title:
            _emb["title"] = self.title

        if self.description:
            _emb["description"] = self.description

        if self.url:
            _emb["url"] = self.url

        if self.timestamp:
            _emb["timestamp"] = self.timestamp

        if self.color:
            _emb["color"] = self.color

        if self.fields:
            _emb["fields"] = self.fields

        if self.footer:
            _emb["footer"] = self.footer

        if self.image:
            _emb["image"] = self.image

        if self.thumbnail:
            _emb["thumbnail"] = self.thumbnail

        if self.video:
            _emb["video"] = self.video

        if self.author:
            _emb["author"] = self.author

        if self.provider:
            _emb["provider"] = self.provider

        return _emb

    def __dict__(self):
        return self.to_dict()

class Color:
    """
    Common color values
    For Discord branding colors, use `BrandingColor`
    """
    white = 0xFFFFFF
    black = 0x000000
    blue = 0x0000FF
    green = 0x00FF00
    red = 0xFF0000
    yellow = 0xFFFF00
    gray = 0x808080
    orange = 0xFF8000
    purple = 0x800080
    cyan = 0x00FFFF

    @staticmethod
    def from_rgb(rgb):
        _hex = '%02x%02x%02x' % rgb
        return Color.from_hex(_hex)
    
    @staticmethod
    def from_hex(_hex):
        return int(_hex, 16)


class BrandingColor:
    """
    Colors, based off of Discord's branding guidelines
    https://discord.com/branding
    """
    blurple = 0x5865F2
    old_blurple = 0x7289DA
    grey = 0x979C9F
    red = 0xED4245
    green = 0x57F287
    yellow = 0xFEE75C
    fuchsia = 0xEB459E
    white = 0xFFFFFF
    black = 0x000000