from dataclasses import dataclass
from typing import List

from bparrot.http import Req


class DictLoader:
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


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
        _hex = "%02x%02x%02x" % rgb
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


@dataclass
class User(DictLoader):
    """
    Represents a resolved Discord User
    """

    id: int
    username: str
    discriminator: str
    avatar: str = None
    bot: bool = False
    system: bool = False
    mfa_enabled: bool = False
    banner: str = None
    accent_color: int = None
    locale: str = None
    verified: bool = False
    email: str = None
    flags: int = None
    premium_type: int = None
    public_flags: int = None


@dataclass
class Member(DictLoader):
    """
    Represents a resolved Discord Member
    """

    roles: List[int]
    joined_at: str

    user: User
    nick: str = None
    avatar: str = None
    premium_since: str = None
    is_pending: bool = None
    pending: bool = None
    permissions: int = None

    def __post_init__(self):

        self.id = self.user.id
        self.name = self.user.username
        self.discriminator = self.user.discriminator
        self.bot = self.user.bot

        self.mention: str = f"<@{self.user.id}>"


@dataclass
class Message(DictLoader):

    id: int
    channel_id: int
    author: User
    content: str
    timestamp: str
    edited_timestamp: str = None
    tts: bool = False
    mention_everyone: bool = False
    mentions: List[User] = None
    mention_roles: List[int] = None
    attachments: List[str] = None
    embeds: List[Embed] = None
    reactions: list = None
    nonce: int = None
    pinned: bool = False
    webhook_id: int = None
    type: int = 0
    activity: dict = None
    application: dict = None
    application_id: int = None
    message_reference: dict = None
    flags: int = None
    referenced_message: dict = None
    interaction: dict = None
    thread: dict = None
    components: list = None
    sticker_items: list = None
    stickers: list = None


class InteractionMessage(Message):

    """
    Represents a Discord message object
    """

    #! Only a shell of a message object, needs more logic

    def __init__(self, _client, inter, data: dict):

        super().__init__(**data)

        self._client = _client
        self._interaction = inter

    async def edit(self, content: str = None):
        data = {}

        if content:
            data["content"] = content

        req = Req(
            "PATCH",
            f"/webhooks/{self.application_id}/{self._interaction.token}/messages/{self.id}",
            json=data,
        )
        resp = await self._client.http_client.request(req)
        return InteractionMessage(self._client, self._interaction, resp)

    async def delete(self):
        req = Req(
            "DELETE",
            f"/webhooks/{self.application_id}/{self._interaction.token}/messages/{self.id}",
        )
        await self._client.http_client.request(req)


class AllowedMentionTypes:
    none = []
    all = ["everyone", "users", "roles"]
    everyone = ["everyone"]
    users = ["users"]
    roles = ["roles"]


class AllowedMentions:
    def __init__(
        self,
        *,
        types: List[AllowedMentionTypes] = [],
        roles: List[int] = [],
        users: List[int] = [],
        replied_user: bool = False,
    ):
        self.types = list(set(types))

        self.roles = list(set(roles))
        if len(self.roles) > 100:
            raise Exception("Maximum of 100 roles ids allowed")

        self.users = list(set(users))
        if len(self.users) > 100:
            raise Exception("Maximum of 100 user ids allowed")

        self.replied_user = replied_user

    @classmethod
    def all(cls, **kwargs):
        return cls(types=AllowedMentionTypes.all, **kwargs)

    @classmethod
    def everyone(cls, **kwargs):
        return cls(types=AllowedMentionTypes.everyone, **kwargs)

    @classmethod
    def users(cls, **kwargs):
        return cls(types=AllowedMentionTypes.users, **kwargs)

    @classmethod
    def roles(cls, **kwargs):
        return cls(types=AllowedMentionTypes.roles, **kwargs)

    def to_dict(self):

        data = {}

        if self.types:
            data["parse"] = self.types

        if self.roles:
            data["roles"] = self.roles

        if self.users:
            data["users"] = self.users

        if self.replied_user:
            data["replied_user"] = self.replied_user

        return data
