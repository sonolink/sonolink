"""MIT License

Copyright (c) 2026-present SonoLink Development Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import abc
import logging
import os
from typing import TYPE_CHECKING, Any, Self, cast, overload

from ..enums import QueueMode
from ._base import BasePlayer, PlayerConnectionState
from ._factory import FrameworkLiteral, PlayerFactory

if TYPE_CHECKING:
    from sonolink.models.filters import Filters
    from sonolink.models.settings import AutoPlaySettings, HistorySettings

    from ..node import Node


__all__ = (
    "BasePlayer",
    "FrameworkLiteral",
    "Player",
    "PlayerConnectionState",
)

_log = logging.getLogger(__name__)


class _PlayerMeta(abc.ABCMeta):
    _factory: PlayerFactory = PlayerFactory()

    @classmethod
    def _adapter(cls) -> type:
        framework = (
            cast(FrameworkLiteral, os.getenv("SONOLINK_FRAMEWORK"))
            or cls._factory.detect_framework()
        )
        return cls._factory.get_player(framework)

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
        **kwargs: Any,
    ) -> type:
        if bases == (BasePlayer,):
            return super().__new__(cls, name, bases, attrs, **kwargs)

        adapter = cls._adapter()
        rewritten = tuple(
            adapter if base is Player else base
            for base in bases
            if base is not BasePlayer
        )

        if adapter not in rewritten:
            rewritten = (
                (rewritten[0], adapter, *rewritten[1:]) if rewritten else (adapter,)
            )

        return super().__new__(cls, name, rewritten, attrs, **kwargs)

    def __instancecheck__(cls, instance: Any) -> bool:
        if cls is Player:
            return type.__instancecheck__(BasePlayer, instance)
        return super().__instancecheck__(instance)

    def __subclasscheck__(cls, subclass: type) -> bool:
        if cls is Player:
            return type.__subclasscheck__(BasePlayer, subclass)
        return super().__subclasscheck__(subclass)


class Player(BasePlayer, metaclass=_PlayerMeta):
    """A dynamic proxy class for SonoLink players.

    Automatically resolves the appropriate :class:`~sonolink.gateway.player._base.BasePlayer`
    implementation for the detected or configured Discord library backend
    (``discord.py``, ``py-cord``, ``disnake``, or ``nextcord``) at instantiation time.

    The framework is resolved from the ``SONOLINK_FRAMEWORK`` environment
    variable, or detected automatically from whichever supported library is
    installed. If no supported framework is found, a :exc:`RuntimeError` is
    raised. If multiple are present, the one already imported is preferred;
    if that is ambiguous, the first available is used and a warning is logged.

    There are two primary ways to create a player:

    1. **Class-pass** — pass the class itself to the voice channel's
       ``connect`` method. The library will instantiate it directly::

           player = await voice_channel.connect(cls=Player)

    2. **Instance-pass** — construct a pre-configured instance and pass it
       instead. The library will call ``player(client, channel)`` which hits
       the concrete adapter's ``__call__``::

           player = Player(node=some_node, volume=80)
           await voice_channel.connect(cls=player)

    Parameters
    ----------
    node : :class:`~sonolink.Node` | None
        The Lavalink node to associate with this player. If ``None``, an
        available node is resolved from the client's node pool at connection
        time.
    queue_mode : :class:`~sonolink.QueueMode`
        The initial queue looping mode. Defaults to ``QueueMode.NORMAL``.
    autoplay_settings : :class:`~sonolink.models.AutoPlaySettings` | None
        AutoPlay configuration. ``None`` uses the default configuration.
        History must be enabled when AutoPlay is active.
    history_settings : :class:`~sonolink.models.HistorySettings` | None
        History configuration. ``None`` uses the default configuration.
    volume : :class:`int` | None
        Initial volume in the range ``0``–``1000``. Defaults to ``100``.
    paused : :class:`bool` | None
        Whether the player should start in a paused state. Defaults to
        ``False``.
    filters : :class:`~sonolink.models.Filters` | None
        Initial audio filters. Defaults to an empty
        :class:`~sonolink.models.Filters` instance.

    Attributes
    ----------
    guild
        The guild this player is attached to. The concrete type depends on
        the underlying Discord library (e.g. :class:`discord:discord.Guild`
        (discord.py), :class:`pycord:discord.Guild` (py-cord),
        :class:`disnake:disnake.Guild` (disnake), or
        :class:`nextcord:nextcord.Guild` (nextcord)).
    channel
        The voice channel this player is currently connected to. The concrete
        type depends on the underlying Discord library.
    client
        The Discord client instance driving this player. The concrete type
        depends on the underlying Discord library.

    """

    if TYPE_CHECKING:

        @overload
        def __new__(cls, client: Any, channel: Any) -> Any: ...

        @overload
        def __new__(
            cls,
            *,
            node: Node | None = None,
            queue_mode: QueueMode = QueueMode.NORMAL,
            autoplay_settings: AutoPlaySettings | None = None,
            history_settings: HistorySettings | None = None,
            volume: int | None = None,
            paused: bool | None = None,
            filters: Filters | None = None,
            **kwargs: Any,
        ) -> Self: ...

        def __new__(cls, *args: Any, **kwargs: Any) -> Any: ...

    else:

        def __new__(cls, *args: Any, **kwargs: Any) -> Any:
            return _PlayerMeta._adapter()(*args, **kwargs)

    def __call__(self, client: Any, channel: Any) -> Any:
        raise NotImplementedError("Player is a proxy; this is never called directly.")

    async def on_voice_server_update(self, data: Any) -> None: ...

    async def on_voice_state_update(self, data: Any) -> None: ...

    def cleanup(self) -> None: ...
