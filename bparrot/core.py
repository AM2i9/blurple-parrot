from typing import List
import logging

from nacl.signing import VerifyKey

from bparrot.interaction import InteractionListener
from bparrot.components import ComponentInteraction, ComponentType
from bparrot.application_commands import (
    MessageCommand,
    SlashCommand,
    SlashOption,
    UserCommand,
)


_log = logging.getLogger("blurple-parrot")


def verify_key(pk: str, body: bytes, signature: str, timestamp: str) -> bool:
    """
    Validate the following headers of an interaction request:
        - X-Signature-Ed25519
        - X-Signature-Timestamp

    https://discord.com/developers/docs/interactions/receiving-and-responding#security-and-authorization
    """

    key = VerifyKey(bytes.fromhex(pk))

    try:
        key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
        return True
    except Exception as e:
        _log.warn(e)
    return False


def slash_command(
    name: str,
    description: str,
    options: List[SlashOption] = [],
    default_permission: bool = True,
):
    """
    Create a SlashCommand Listener. Used as a decorator. Takes the same
    parameters as a SlashCommand object. Must be manually added to the Client.
    """

    def _deco(func):
        _cmd = SlashCommand(
            name=name,
            description=description,
            options=options,
            default_permission=default_permission,
        )
        _listener = InteractionListener(_cmd, func)
        return _listener

    return _deco


def user_command(name: str):
    """
    Create a UserCommand Listener. Used as a decorator. Takes only the `name`
    parameter. Must be manually added to the Client.
    """

    def _deco(func):
        _cmd = UserCommand(name)
        _listener = InteractionListener(_cmd, func)
        return _listener

    return _deco


def message_command(name: str):
    """
    Create a MessageCommand Listener. Used as a decorator. Takes only the `name`
    parameter. Must be manually added to the Client.
    """

    def _deco(func):
        _cmd = MessageCommand(name)
        _listener = InteractionListener(_cmd, func)
        return _listener

    return _deco


def button(custom_id: str):
    """
    Create a ComponentIteraction Listener that is listening for a Button of a
    certain `custom_id`. Must be manually added to the Client.
    """

    def _deco(func):
        _cmp = ComponentInteraction(
            custom_id=custom_id, component_type=ComponentType.BUTTON
        )
        _listener = InteractionListener(_cmp, func)
        return _listener

    return _deco


def select(custom_id: str):
    """
    Create a ComponentIteraction Listener that is listening for a SelectMenu of
    a certain `custom_id`. Must be manually added to the Client.
    """

    def _deco(func):
        _cmp = ComponentInteraction(
            custom_id=custom_id, component_type=ComponentType.SELECT_MENU
        )
        _listener = InteractionListener(_cmp, func)
        return _listener

    return _deco
