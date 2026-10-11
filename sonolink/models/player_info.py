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

from sonolink.utils import cached_property

from ..rest.schemas.player import (
    Player as PlayerInfoPayload,
    PlayerFilters,
    PlayerState,
    PlayerVoiceState,
)
from .base import BaseModel
from .track import Playable

__all__ = ("PlayerInfo",)


class PlayerInfo(BaseModel[PlayerInfoPayload]):
    """Represents a player's info data.

    This class wraps the raw :class:`sonolink.rest.schemas.Player` schema and provides
    a high-level interface for accessing player metadata and state.
    """

    __slots__ = ("_cs_track",)

    @property
    def guild_id(self) -> int:
        """The Discord guild ID the player belongs to."""
        return int(self._data.guild_id)

    @cached_property("_cs_track")
    def track(self) -> Playable | None:
        """Return the current playing track, or ``None`` if no track is playing."""
        track = self._data.track
        if not track:
            return None
        assert self._client
        return Playable(client=self._client, data=track)

    @property
    def volume(self) -> int:
        """The player volume in a 0-1000 percent scale."""
        return self._data.volume

    @property
    def paused(self) -> bool:
        """Whether the player is currently paused."""
        return self._data.paused

    @property
    def state(self) -> PlayerState:
        """The current state of the player (:class:`~sonolink.rest.schemas.player.PlayerState`)."""
        return self._data.state

    @property
    def position(self) -> int:
        """Current track position in milliseconds."""
        return self._data.state.position

    @property
    def connected(self) -> bool:
        """Whether the player is connected to a voice channel."""
        return self._data.state.connected

    @property
    def ping(self) -> int:
        """The connection ping in milliseconds.

        Returns ``-1`` if the player is not connected.
        """
        return self._data.state.ping

    @property
    def voice(self) -> PlayerVoiceState:
        """The voice connection state of the player (:class:`~sonolink.rest.schemas.player.PlayerVoiceState`)."""
        return self._data.voice

    @property
    def channel_id(self) -> int | None:
        """The Discord voice channel ID the player is connected to.

        Returns ``None`` if the player is not connected to a channel.
        """
        channel_id = self._data.voice.channel_id
        if channel_id is None:
            return None
        return int(channel_id)

    @property
    def filters(self) -> PlayerFilters:
        """The audio filters currently applied to the player."""
        return self._data.filters
