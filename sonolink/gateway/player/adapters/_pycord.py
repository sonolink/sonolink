"""Apache License 2.0

Copyright (c) 2026-present SonoLink Development Team.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Self, cast, overload

import discord
from discord.voice import VoiceProtocol

from sonolink.gateway.enums import QueueMode
from sonolink.models.filters import Filters

from .._base import BasePlayer

if TYPE_CHECKING:
    from discord.raw_models import (
        RawVoiceServerUpdateEvent as VoiceServerUpdate,
        RawVoiceStateUpdateEvent as VoiceStateUpdate,
    )

    from sonolink.gateway.node import Node
    from sonolink.models.settings import AutoPlaySettings, HistorySettings

_log = logging.getLogger(__name__)
UNSET = discord.utils.MISSING


__all__ = ("PycordPlayer",)


class PycordPlayer(BasePlayer, VoiceProtocol[discord.Client]):
    """A py-cord implementation of :class:`~sonolink.gateway.player._base.BasePlayer`.

    This class satisfies the :class:`discord.voice.VoiceProtocol` contract expected
    by py-cord's voice connection machinery, whilst delegating all Lavalink playback
    logic to the handlers initialised by :class:`BasePlayer`.

    There are two primary ways to create a player:

    1. **Class-pass** - pass the class itself to
       :meth:`discord.abc.Connectable.connect`. py-cord will instantiate it
       by calling ``Player(client, channel)``::

            player = await voice_channel.connect(cls=Player)

    2. **Instance-pass** - construct a pre-configured instance and pass it
       instead. py-cord will call ``player(client, channel)`` which hits
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
        The py-cord client driving this player.
    """

    channel: discord.abc.Connectable
    client: discord.Client

    _guild: discord.Guild | None

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
            super(BasePlayer, self).__init__(client, channel)
            if isinstance(channel, discord.abc.GuildChannel):
                self._guild = channel.guild

    def __call__(
        self,
        client: discord.Client,
        channel: discord.abc.Connectable,
    ) -> Self:
        """Bind the player when a pre-configured **instance** is passed to
        :meth:`discord.abc.Connectable.connect`.

        Binds the py-cord ``VoiceProtocol`` attributes, resolves the guild
        from the channel, and registers the player with its node.

        Parameters
        ----------
        client: :class:`discord.Client`
            The py-cord client instance.
        channel: :class:`discord.abc.Connectable`
            The voice channel being connected to.

        Returns
        -------
        :class:`Player`
            This player instance, fully initialised.
        """
        super(BasePlayer, self).__init__(client, channel)

        if isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
            self._guild = channel.guild

        self._ensure_node()
        return self

    async def on_voice_server_update(self, data: VoiceServerUpdate) -> None:
        return await self._events_handler.on_voice_server_update(
            cast(dict[str, Any], data._raw_data)
        )

    async def on_voice_state_update(self, data: VoiceStateUpdate) -> None:
        return await self._events_handler.on_voice_state_update(
            cast(dict[str, Any], data._raw_data)
        )

    def cleanup(self) -> None:
        super(BasePlayer, self).cleanup()
