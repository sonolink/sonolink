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

from typing import Any

import msgspec

from .filters import PlayerFilters
from .track import Track

__all__ = (
    "DestroyPlayerResponse",
    "GetPlayerResponse",
    "GetPlayersResponse",
    "Player",
    "PlayerState",
    "PlayerVoiceState",
    "UpdatePlayerRequest",
    "UpdatePlayerResponse",
    "UpdatePlayerTrackRequest",
)


class Player(msgspec.Struct, kw_only=True):
    """Represents a Lavalink Player."""

    guild_id: str = msgspec.field(name="guildId")
    """The Discord guild ID the player belongs to."""

    track: Track | None = None
    """Currently playing track (:class:`Track`) or ``None`` if no track is loaded."""

    volume: int
    """Player volume (0-1000 percent scale)."""

    paused: bool
    """Whether the player is currently paused."""

    state: PlayerState
    """Current state of the player (:class:`PlayerState`)."""

    voice: PlayerVoiceState
    """Voice connection state (:class:`PlayerVoiceState`)."""

    filters: PlayerFilters
    """Active audio filters (:class:`PlayerFilters`)."""


class PlayerState(msgspec.Struct, kw_only=True):
    """Represents the state of a Lavalink Player."""

    time: int
    """Timestamp of the state in milliseconds."""

    position: int
    """Current track position in milliseconds."""

    connected: bool
    """Whether the player is connected to a voice channel."""

    ping: int
    """Connection ping in milliseconds, ``-1`` if not connected."""


class PlayerVoiceState(msgspec.Struct, kw_only=True):
    """Represents the voice connection state of a Lavalink Player."""

    token: str
    """Voice connection token."""

    endpoint: str
    """Voice server endpoint."""

    session_id: str = msgspec.field(name="sessionId")
    """Session ID of the voice connection."""

    channel_id: str | None = msgspec.field(name="channelId", default=None)
    """The Discord voice channel ID the bot is connecting to."""


class UpdatePlayerRequest(msgspec.Struct, kw_only=True):
    """Payload to update a Lavalink Player.

    This object is sent to `/players/{guildId}` to modify player state.
    """

    track: UpdatePlayerTrackRequest | msgspec.UnsetType = msgspec.UNSET
    """Track to play or update (:class:`UpdatePlayerTrackRequest`), optional."""

    position: int | msgspec.UnsetType = msgspec.UNSET
    """Seek position in milliseconds, optional."""

    endtime: int | msgspec.UnsetType = msgspec.field(
        name="endTime", default=msgspec.UNSET
    )
    """Track end time in milliseconds, optional."""

    volume: int | msgspec.UnsetType = msgspec.UNSET
    """Volume to set (0-1000 percent scale), optional."""

    paused: bool | msgspec.UnsetType = msgspec.UNSET
    """Whether to pause the player, optional."""

    filters: PlayerFilters | msgspec.UnsetType = msgspec.UNSET
    """Audio filters to apply (:class:`PlayerFilters`), optional."""

    voice: PlayerVoiceState | msgspec.UnsetType = msgspec.UNSET
    """Voice state updates (:class:`PlayerVoiceState`), optional."""


class UpdatePlayerTrackRequest(msgspec.Struct, kw_only=True):
    """Represents a track update request for a Lavalink Player.

    Used within :class:`UpdatePlayerRequest` to play or modify a track.
    """

    encoded: str | msgspec.UnsetType | None = msgspec.UNSET
    """Base64-encoded track string, optional."""

    identifier: str | msgspec.UnsetType = msgspec.UNSET
    """Unique track identifier, optional."""

    user_data: dict[str, Any] | msgspec.UnsetType = msgspec.field(
        name="userData", default=msgspec.UNSET
    )
    """Optional user data previously provided when updating the player."""


type GetPlayersResponse = list[Player]
"""Response type for GET /players. Returns a list of :class:`Player` objects."""

type GetPlayerResponse = Player
"""Response type for GET /players/{guildId}. Returns a single :class:`Player` object."""

type UpdatePlayerResponse = Player
"""Response type for PATCH /players/{guildId}. Returns the updated :class:`Player` object."""

type DestroyPlayerResponse = None
"""Response type for DELETE /players/{guildId}. Returns nothing on success."""
