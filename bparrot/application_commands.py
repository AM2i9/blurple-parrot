from bparrot.models import Member, Message, User
import re

from typing import List


class CommandNameError(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return (
            f"Name {self.name} should only contain the following symbols: a-z 0-9 - _"
        )


class SlashOptionType:
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10


class ApplicationCommandType:
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3


class ApplicationCommand:

    name: str

    def __init__(self, type: ApplicationCommandType, guild_id: int = None, **kwargs):
        self.type = type
        self.id = kwargs.get("id", 0)
        self.guild_id = guild_id
        self.application_id = kwargs.get("application_id", None)

        self.options = []

    def __eq__(self, other):
        return (self.id == other.id) or (
            self.type == other.type
            and self.name == other.name
            and all([option in self.options for option in other.options])
        )

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class SlashChoice:
    def __init__(self, name: str, value):
        self.name = name
        self.value = value

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return {"name": self.name, "value": self.value}


class SlashOption:
    def __init__(
        self,
        name: str,
        description: str = "",
        type: SlashOptionType = SlashOptionType.STRING,
        required: bool = False,
        choices: List[SlashChoice] = [],
        options: List["SlashOption"] = [],
        value=None,
    ):

        if re.match("^[\w-]{1,32}$", name) is None and name.islower():
            raise CommandNameError(name)

        self.name = name
        self.description = description
        self.type = type
        self.required = bool(required)
        self.choices = choices
        self.options = options

        if value is not None:
            self.value = value

    def __eq__(self, other):
        return self.type == other.type and self.name == other.name

    @classmethod
    def from_dict(cls, data):
        if data.get("choices"):
            data["choices"] = [
                SlashChoice.from_dict(choice) for choice in data["choices"]
            ]
        if data.get("options"):
            data["options"] = [
                SlashOption.from_dict(option) for option in data["options"]
            ]
        return cls(**data)

    def to_dict(self):
        data = {
            "type": self.type,
            "name": self.name,
            "description": self.description,
        }

        if self.required:
            data["required"] = self.required

        if self.choices:
            data["choices"] = [c.to_dict() for c in self.choices]

        if self.options:
            data["options"] = [o.to_dict() for o in self.options]

        return data


class SlashCommand(ApplicationCommand):
    def __init__(
        self,
        name: str,
        description: str = "",
        *,
        options: List[SlashOption] = [],
        default_permission: bool = True,
        **kwargs,
    ):
        super().__init__(ApplicationCommandType.CHAT_INPUT, **kwargs)

        if re.match("^[\w-]{1,32}$", name) is None and name.islower():
            raise CommandNameError(name)

        self.name = name
        self.description = description
        self.options = options
        self.default_permission = default_permission

    @classmethod
    def from_dict(cls, data):
        if data.get("options"):
            data["options"] = [
                SlashOption.from_dict(option) for option in data["options"]
            ]
        return cls(**data)

    def to_dict(self):
        data = {
            "type": self.type,
            "name": self.name,
            "description": self.description,
        }

        if self.options:
            data["options"] = [o.to_dict() for o in self.options]
        if not self.default_permission:
            data["default_permission"] = False

        return data


class UserCommand(ApplicationCommand):
    def __init__(self, name: str, **kwargs):
        super().__init__(ApplicationCommandType.USER, **kwargs)
        self.name = name

        resolved = kwargs.get("resolved")
        if resolved:
            raw_member = list(resolved.get("members").values())[0]
            raw_user = list(resolved.get("users").values())[0]

            self.user = User.from_dict(raw_user)
            raw_member["user"] = self.user
            self.member = Member.from_dict(raw_member)

    def to_dict(self):
        return {"type": self.type, "name": self.name}


class MessageCommand(ApplicationCommand):
    def __init__(self, name: str, **kwargs):
        super().__init__(ApplicationCommandType.MESSAGE, **kwargs)
        self.name = name
    
        resolved = kwargs.get("resolved")
        if resolved:
            raw_message = list(resolved.get("messages").values())[0]
            self.resolved_message = Message.from_dict(raw_message)

    def to_dict(self):
        return {"type": self.type, "name": self.name}


def get_application_command(data: dict) -> ApplicationCommand:
    type_ = data.pop("type")
    if type_ == ApplicationCommandType.CHAT_INPUT:
        return SlashCommand.from_dict(data)
    elif type_ == ApplicationCommandType.USER:
        return UserCommand.from_dict(data)
    elif type_ == ApplicationCommandType.MESSAGE:
        return MessageCommand.from_dict(data)
    else:
        return None
