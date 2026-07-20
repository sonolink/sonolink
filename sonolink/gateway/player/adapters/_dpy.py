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

import logging
from typing import TYPE_CHECKING, Any, Self, cast, overload

import discord

from sonolink.gateway.enums import QueueMode
from sonolink.models.filters import Filters

from .._base import BasePlayer

if TYPE_CHECKING:
    from discord.types.voice import GuildVoiceState, VoiceServerUpdate

    from sonolink.gateway.node import Node
    from sonolink.models.settings import AutoPlaySettings, HistorySettings

_log = logging.getLogger(__name__)
UNSET = discord.utils.MISSING


__all__ = ("DpyPlayer",)


class DpyPlayer(BasePlayer, discord.VoiceProtocol):
    """A discord.py implementation of :class:`~sonolink.gateway.player._base.BasePlayer`.

    This class satisfies the :class:`discord.VoiceProtocol` contract expected
    by discord.py's voice connection machinery, whilst delegating all Lavalink
    playback logic to the handlers initialised by :class:`BasePlayer`.

    There are two primary ways to create a player:

    1. **Class-pass** — pass the class itself to
       :meth:`discord.abc.Connectable.connect`. discord.py will instantiate it
       by calling ``Player(client, channel)``::

           player = await voice_channel.connect(cls=Player)

    2. **Instance-pass** — construct a pre-configured instance and pass it
       instead. discord.py will call ``player(client, channel)`` which hits
       ``__call__``::

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
    guild : :class:`discord.Guild`
        The guild this player is attached to.
    channel : :class:`discord.VoiceChannel` | :class:`discord.StageChannel`
        The voice channel this player is currently connected to.
    client : :class:`discord.Client`
        The discord.py client driving this player.
    """

    channel: discord.abc.Connectable
    client: discord.Client

    _guild: discord.Guild | None

    if TYPE_CHECKING:

        @property
        def guild(self) -> discord.Guild: ...

    @overload
    def __init__(
        self,
        *,
        node: Node | None = ...,
        queue_mode: QueueMode = ...,
        autoplay_settings: AutoPlaySettings | None = ...,
        history_settings: HistorySettings | None = ...,
        volume: int | None = ...,
        paused: bool | None = ...,
        filters: Filters | None = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        client: discord.Client,
        channel: discord.abc.Connectable,
    ) -> None: ...

    def __init__(
        self,
        client: discord.Client = UNSET,
        channel: discord.abc.Connectable = UNSET,
        *,
        node: Node | None = None,
        queue_mode: QueueMode = QueueMode.NORMAL,
        autoplay_settings: AutoPlaySettings | None = None,
        history_settings: HistorySettings | None = None,
        volume: int | None = None,
        paused: bool | None = None,
        filters: Filters | None = None,
    ) -> None:
        super().__init__(
            node=node,
            queue_mode=queue_mode,
            autoplay_settings=autoplay_settings,
            history_settings=history_settings,
            volume=volume,
            paused=paused,
            filters=filters,
        )

        self._guild = None

        if client is not UNSET and channel is not UNSET:
            discord.VoiceProtocol.__init__(self, client=client, channel=channel)
            if isinstance(channel, discord.abc.GuildChannel):
                self._guild = channel.guild
            self._ready = True

    def __call__(
        self,
        client: discord.Client,
        channel: discord.abc.Connectable,
    ) -> Self:
        """Bind the player when a pre-configured **instance** is passed to
        :meth:`discord.abc.Connectable.connect`.

        Binds the discord.py ``VoiceProtocol`` attributes, resolves the guild
        from the channel, and registers the player with its node.

        Parameters
        ----------
        client : :class:`discord.Client`
            The discord.py client instance.
        channel : :class:`discord.abc.Connectable`
            The voice channel being connected to.

        Returns
        -------
        :class:`DpyPlayer`
            This player instance, fully initialised.
        """
        discord.VoiceProtocol.__init__(self, client=client, channel=channel)

        if isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
            self._guild = channel.guild

        self._ensure_node()
        return self

    async def on_voice_server_update(self, data: VoiceServerUpdate) -> None:
        """Handle a ``VOICE_SERVER_UPDATE`` payload from the Discord gateway.

        Provides the voice server token and endpoint to the Lavalink node so
        it can establish or re-establish the audio stream.

        Parameters
        ----------
        data : :class:`discord.types.voice.VoiceServerUpdate`
            The raw payload received from the Discord gateway.
        """
        await self._events_handler.on_voice_server_update(cast(dict[str, Any], data))

    async def on_voice_state_update(self, data: GuildVoiceState) -> None:
        """Handle a ``VOICE_STATE_UPDATE`` payload from the Discord gateway.

        Provides the session ID and channel ID required for the voice
        connection handshake with the Lavalink node.

        Parameters
        ----------
        data : :class:`discord.types.voice.GuildVoiceState`
            The raw payload received from the Discord gateway.
        """
        await self._events_handler.on_voice_state_update(cast(dict[str, Any], data))

    def cleanup(self) -> None:
        discord.VoiceProtocol.cleanup(self)
