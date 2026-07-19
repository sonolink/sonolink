"""MIT License

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

from enum import Enum, StrEnum

__all__ = (
    "AutoPlayMode",
    "DisconnectTriggerType",
    "InactivityMode",
    "NodeRegion",
    "NodeStatus",
    "QueueMode",
    "SearchProvider",
    "ShuffleMode",
    "TrackEndReason",
    "TrackExceptionSeverity",
)


class AutoPlayMode(StrEnum):
    """Enum representing the autoplay behavior of the player.

    :ivar ENABLED: AutoPlay works fully autonomously and fills the auto_queue with recommended tracks.
        If a track is added to the player's standard queue, AutoPlay will treat it as a priority.
    :ivar PARTIAL: AutoPlay works autonomously but does **not** fill the auto_queue with recommended tracks.
    :ivar DISABLED: AutoPlay is completely disabled and will not perform any automatic actions.
    """

    ENABLED = "enabled"
    PARTIAL = "partial"
    DISABLED = "disabled"


class DisconnectTriggerType(Enum):
    """Enum representing what triggered a disconnect from a Player.

    :ivar MANUAL: The disconnect was triggered manually, usually by calling :meth:`Player.disconnect`.
    :ivar INACTIVITY: The disconnect was triggered by the inactivity handler.
    :ivar ERROR: The disconnect was triggered due to an error.
    :ivar UNKNOWN: The disconnect was triggered by an unknown source.
    """

    MANUAL = 1
    INACTIVITY = 2
    ERROR = 3
    UNKNOWN = 4


class InactivityMode(Enum):
    """Represents the mode used to determine if a player is inactive.

    :ivar ALL_BOTS: The player is considered inactive if no non-bot members are in the voice channel.
    :ivar ONLY_SELF: The player is considered inactive only if it is the only member in the voice channel.
    :ivar IGNORED_USERS: The player is considered inactive if none of the specified "Keep Alive" user IDs are in the voice channel.
    """

    ALL_BOTS = 1
    ONLY_SELF = 2
    IGNORED_USERS = 3


class NodeStatus(Enum):
    """Represents the connection status of a node.

    :ivar DISCONNECTED: The node is not connected to Lavalink.
    :ivar CONNECTED: The node is connected to Lavalink.
    :ivar CONNECTING: The node is in the process of connecting to Lavalink.
    """

    DISCONNECTED = 1
    CONNECTED = 2
    CONNECTING = 3


class QueueMode(StrEnum):
    """Enum representing the various modes on :class:`sonolink.Queue`.

    :ivar NORMAL: Normal queue mode. Tracks are played in the order they were added.
    :ivar LOOP: Loop the current track indefinitely. The next track will not be played until the current track is stopped or replaced.
    :ivar LOOP_ALL: Loop the entire queue indefinitely. Once the queue is empty, it will be refilled with the tracks in the
        history (if enabled) and playback will continue. If history is not enabled, the queue will simply start over
        with the original tracks.
    """

    NORMAL = "normal"
    LOOP = "loop"
    LOOP_ALL = "loop_all"


class ShuffleMode(StrEnum):
    """Enum representing the shuffle state of a :class:`sonolink.Queue`.

    Independent of :class:`QueueMode`; composes with any of its values.

    .. versionadded:: 1.3.0

    :ivar ENABLED: A random track is popped from the queue each time one is needed,
        without reordering the underlying queue. Toggling back to ``DISABLED`` resumes
        in-order playback with the original order intact.
    :ivar DISABLED: Shuffle is disabled. Tracks are played in queue order.
    """

    ENABLED = "enabled"
    DISABLED = "disabled"


class SearchProvider(StrEnum):
    """Enum representing search providers for AutoPlay.

    :ivar YOUTUBE: YouTube Radio (RD) mix based on a video identifier.
    :ivar SPOTIFY: Spotify recommendations based on a track identifier.
    :ivar DEEZER: Deezer track/artist radio based on an identifier.
    """

    YOUTUBE = "https://www.youtube.com/watch?v={identifier}&list=RD{identifier}"
    SPOTIFY = "sprec:{identifier}"
    DEEZER = "dzrec:{identifier}"


class TrackEndReason(StrEnum):
    """Represents the ``reason`` field from a track-end event payload.

    :ivar FINISHED: The track finished playing.
    :ivar LOAD_FAILED: The track failed to load.
    :ivar STOPPED: The track was stopped.
    :ivar REPLACED: The track was replaced.
    :ivar CLEANUP: The track was cleaned up.
    """

    FINISHED = "finished"
    LOAD_FAILED = "loadFailed"
    STOPPED = "stopped"
    REPLACED = "replaced"
    CLEANUP = "cleanup"

    @property
    def can_start_next(self) -> bool:
        """Whether the next track can start playing."""
        return self not in (
            TrackEndReason.STOPPED,
            TrackEndReason.REPLACED,
            TrackEndReason.CLEANUP,
        )


class TrackExceptionSeverity(StrEnum):
    """Represents a TrackException's error severity.

    :ivar COMMON: The cause is known and expected, indicates that there
        is nothing wrong with the library itself.
    :ivar SUSPICIOUS: The cause might not be exactly known, but is possibly
        caused by outside factors. For example when an outside service responds
        in a format that we do not expect.
    :ivar FAULT: The probable cause is an issue with the library or there is
        no way to tell what the cause might be. This is the default level and
        other levels are used in cases where the thrower has more in-depth
        knowledge about the error.
    """

    COMMON = "common"
    SUSPICIOUS = "suspicious"
    FAULT = "fault"


class NodeRegion(StrEnum):
    """Represents the available regions of a node.

    .. versionadded:: 1.2.0

    :ivar BRAZIL: Brazil
    :ivar HONG_KONG: Hong Kong
    :ivar INDIA: India
    :ivar JAPAN: Japan
    :ivar ROTTERDAM: Rotterdam
    :ivar SINGAPORE: Singapore
    :ivar SOUTH_AFRICA: South Africa
    :ivar SYDNEY: Sydney
    :ivar US_EAST: US East
    :ivar US_WEST: US West
    :ivar US_CENTRAL: US Central
    :ivar US_SOUTH: US South
    """

    BRAZIL = "brazil"
    HONG_KONG = "hongkong"
    INDIA = "india"
    JAPAN = "japan"
    ROTTERDAM = "rotterdam"
    SINGAPORE = "singapore"
    SOUTH_AFRICA = "southafrica"
    SYDNEY = "sydney"
    US_EAST = "us-east"
    US_WEST = "us-west"
    US_CENTRAL = "us-central"
    US_SOUTH = "us-south"
