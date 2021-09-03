import asyncio
from aiohttp.web_app import Application

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
    def __init__(self, data: dict):

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
    
    def create_response(
        self,
        type_: int = 4,
        content: str = "",
        embed = None,
        embeds: list = None,
        allowed_mentions=None,
        flags: int = None,
        components: list = None,
        empheral: bool = False,
    ):
        data = {}

        if content is not None:
            data["content"] = content
        
        resp = {
            "type": type_,
            "data": data
        }

        return resp
        
