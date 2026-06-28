"""
MIT License

Copyright (c) 2026-present SonoLink Development Team.

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

import datetime

import msgspec

__all__ = (
    "CPUStats",
    "FrameStats",
    "MemoryStats",
    "PlayerState",
    "PlayerUpdateEvent",
    "ReadyEvent",
    "StatsEvent",
    "WebSocketClosedEvent",
)


class ReadyEvent(msgspec.Struct):
    """Represents a Ready event received via the websocket."""

    resumed: bool
    """Whether the session was resumed, if this is ``False`` it implies a new connection
    was created.
    """
    session_id: str = msgspec.field(name="sessionId")
    """The secret session ID."""


class PlayerUpdateEvent(msgspec.Struct):
    """Represents a Player Update event received via the websocket."""

    _guild_id: str = msgspec.field(name="guildId")
    state: PlayerState
    """The state of the player."""

    @property
    def guild_id(self) -> int:
        """The guild ID of the player."""
        return int(self._guild_id)


class PlayerState(msgspec.Struct):
    """Represents a Player state on a Player Update event."""

    _time: int = msgspec.field(name="time")
    position: int
    """The position of the track in milliseconds."""
    connected: bool
    """Whether a connection is established."""
    ping: int
    """The ping of the connection node to the voice server in milliseconds.
    If this is ``-1``, it has not been yet connected.
    """

    @property
    def time(self) -> datetime.datetime:
        """The timestamp of when this state is from."""
        return datetime.datetime.fromtimestamp(self._time / 1000)


class StatsEvent(msgspec.Struct):
    """Represents the statistics received every minute via the websocket."""

    players: int
    """The players count attached to the node."""
    playing_players: int = msgspec.field(name="playingPlayers")
    """The players count attached to the node that are playing a track.."""
    uptime: int
    """The node uptime in milliseconds."""
    memory: MemoryStats
    """The memory stats of the node."""
    cpu: CPUStats
    """The CPU stats of the node."""
    frame_stats: FrameStats | None = msgspec.field(name="frameStats", default=None)
    """The frame stats of the node."""


class MemoryStats(msgspec.Struct):
    """Represents the stats of the memory of the machine received within a stats event."""

    free: int
    """The amount of free memory in bytes."""
    used: int
    """The amount of used memory in bytes."""
    allocated: int
    """The amount of allocated memory in bytes."""
    reservable: int
    """The amount of reservable memory in bytes."""


class CPUStats(msgspec.Struct):
    """Represents the stats of the CPU of the machine received within a stats event."""

    cores: int
    """The amount of cores the node has."""
    system_load: float = msgspec.field(name="systemLoad")
    """The system load of the node."""
    lavalink_load: float = msgspec.field(name="lavalinkLoad")
    """The load of lavalink on the node."""


class FrameStats(msgspec.Struct):
    """Represents the audio frames stats of the players received within a stats event."""

    sent: int
    """The amount of frames sent to Discord."""
    nulled: int
    """The amount of frames that were nulled."""
    deficit: int
    """The difference between sent frames and the expected amount of frames.
    If this number is negative, too many frames were sent, and if it's positive, not
    enough frames are being sent.
    """


class WebSocketClosedEvent(msgspec.Struct):
    """Represents the websocket closed event received when an audio WebSocket to Discord is terminated."""

    code: int
    """The Discord close event code."""
    reason: str
    """The reason why the connection was closed."""
    by_remote: bool = msgspec.field(name="byRemote")
    """Whether the closure was made by Discord."""
