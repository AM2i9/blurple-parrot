from typing import List


class ComponentValueError(Exception):
    def __init__(self, message: str, component):
        self.message = message
        self.component = component

    def __str__(self) -> str:
        return self.message


class ComponentType:
    ACTION_ROW = 1
    BUTTON = 2
    SELECT_MENU = 3


class ButtonStyle:
    """
    Button component styles.
    https://discord.com/developers/docs/interactions/message-components#button-object-button-styles
    """

    # Style names
    primary = 1
    secondary = 2
    success = 3
    danger = 4
    link = 5

    # Color names
    blurple = 1
    grey = 2
    green = 3
    red = 4


class MessageComponent:
    """
    A Discord message component.
    """

    def to_dict(self) -> dict:
        data = {key: value for key, value in vars(self).items() if value}

        if data.get("options"):
            data["options"] = [o.to_dict() for o in data["options"]]

        if data.get("components"):
            data["components"] = [c.to_dict() for c in data["components"]]

        return data


class Button(MessageComponent):
    """
    A Discord button component.

    Non-link buttons must have a custom_id, and cannot have a url.
    Link buttons must have a url, and cannot have a custom_id.
    Link buttons do not send an interaction to your app when clicked
    """

    def __init__(
        self,
        style: str = ButtonStyle.primary,
        custom_id: str = None,
        label: str = None,
        emoji=None,
        url: str = None,
        disabled: bool = False,
    ):

        self.style = style
        self.type = ComponentType.BUTTON

        self.url = url
        self.custom_id = custom_id

        self.label = label
        self.emoji = emoji
        self.disabled = bool(disabled)

        if style == ButtonStyle.link:
            if url is None:
                raise ComponentValueError("Link style buttons must have a URL", self)
            if custom_id:
                raise ComponentValueError(
                    "Link style buttons cannot have a custom ID", self
                )
        else:
            if url is not None:
                raise ComponentValueError(
                    "Non-link style buttons cannot have a URL", self
                )
            if not custom_id:
                raise ComponentValueError(
                    "Non-link style buttons must have a custom ID"
                )

        if custom_id and len(custom_id) > 100:
            raise ComponentValueError(
                "Custom ID cannot be longer than 100 characters", self
            )

        if label and len(label) > 80:
            raise ComponentValueError("Label cannot be longer than 80 characters", self)

        if not label and not emoji:
            raise ComponentValueError("Button must have either a label or emoji", self)


class SelectOption(MessageComponent):
    """
    A Discord Select Option for the Select Menu.
    """

    def __init__(
        self,
        label: str,
        value: str,
        description: str = None,
        emoji=None,
        default: bool = None,
    ):

        self.label = label
        self.value = value

        self.description = description
        self.emoji = emoji
        self.default = bool(default)

        if len(label) > 100:
            raise ComponentValueError("Label cannot be longer than 100 characters")

        if len(value) > 100:
            raise ComponentValueError("Value cannot be longer than 100 characters")

        if description and len(description) > 100:
            raise ComponentValueError(
                "Description cannot be longer than 100 characters"
            )


class SelectMenu(MessageComponent):
    """
    A Discord Select Menu.
    """

    def __init__(
        self,
        custom_id: str,
        options: List,
        placeholder: str = None,
        min_values: int = None,
        max_values: int = None,
        disabled: bool = False,
    ):
        self.type = ComponentType.SELECT_MENU

        self.custom_id = custom_id
        self.placeholder = placeholder

        self.options = options

        self.min_values = min_values

        self.max_values = max_values
        self.disabled = bool(disabled)

        if len(custom_id) > 100:
            raise ComponentValueError("Custom ID cannot be longer than 100 characters")

        if placeholder and len(placeholder) > 100:
            raise ComponentValueError("Custom ID cannot be longer than 100 characters")

        if len(options) > 25:
            raise ComponentValueError("Select Menu cannot have more than 25 options")

        if min_values and not (0 <= min_values <= 25):
            raise ComponentValueError("min_values must be between 0 and 25")

        if max_values and not (max_values <= 25):
            raise ComponentValueError("max_values must be less than 25")


class ActionRow(MessageComponent):
    """
    Represents a Discord Action Row. Action Rows must be used to display
    components. They can contain a maximum of 5 components. An Action Row
    containing buttons cannot also contain a select menu.
    """

    def __init__(self, components):
        self.type = ComponentType.ACTION_ROW

        if len(components) > 5:
            raise ComponentValueError("Action row can have at most 5 components.")

        if not (
            all((isinstance(c, Button) for c in components))
            or all((isinstance(c, SelectMenu) for c in components))
        ):
            raise ComponentValueError(
                "Action row must contain only either Buttons or a Select Menu"
            )

        if len(components) > 1 and all((isinstance(c, SelectMenu) for c in components)):
            raise ComponentValueError("Action row cannot contain one Select Menu")

        self.components = components


class ComponentInteraction:
    def __init__(
        self, custom_id: str, component_type: ComponentType, values: List["str"] = []
    ):
        self.custom_id = custom_id
        self.component_type = component_type
        self.values = values

    def __eq__(self, other):
        return (
            self.custom_id == other.custom_id
            and self.component_type == other.component_type
        )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
