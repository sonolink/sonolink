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

from enum import StrEnum

__all__ = (
    "ExceptionSeverity",
    "IPBlockType",
    "RoutePlannerType",
    "TrackLoadResult",
    "TrackSourceType",
)


class ExceptionSeverity(StrEnum):
    """Exception severity type.

    :ivar COMMON: The cause is known and expected, indicates that there is nothing wrong with the library itself.
    :ivar SUSPICIOUS: The cause might not be exactly known, but is possibly caused by outside factors.
    :ivar FAULT: The probable cause is an issue with the library or there is no way to tell what the cause might be.
    """

    COMMON = "common"
    SUSPICIOUS = "suspicious"
    FAULT = "fault"


class TrackLoadResult(StrEnum):
    """Result type returned when loading tracks.

    Each value represents the type of result returned in
    :attr:`sonolink.rest.schemas.TrackLoadingResponse.load_type`.

    :ivar TRACK: A single track was loaded
    :ivar PLAYLIST: A playlist was loaded
    :ivar SEARCH: Search results were returned
    :ivar EMPTY: No matches for the identifier
    :ivar ERROR: Loading failed
    """

    TRACK = "track"
    PLAYLIST = "playlist"
    SEARCH = "search"
    EMPTY = "empty"
    ERROR = "error"


class TrackSourceType(StrEnum):
    """A track source type. This can be used when searching using
    :meth:`sonolink.Node.search_track` or :meth:`sonolink.Client.search_track`.

    This provides the default track sources by Lavalink.
    """

    YOUTUBE = "ytsearch"
    YOUTUBE_MUSIC = "ytmsearch"
    SOUND_CLOUD = "scsearch"
    SPOTIFY = "spsearch"
    DEEZER = "dzsearch"


class RoutePlannerType(StrEnum):
    """IP route planner strategy used by Lavalink.

    Determines how IP addresses are rotated or balanced
    to handle bans, load, and IPv6 blocks.

    :ivar ROTATING_IP: Switch IP on ban (IPv4 or small IPv6 ranges).
    :ivar NANO_IP: Rotate periodically within a single /64 IPv6 block.
    :ivar ROTATING_NANO_IP: Rotate periodically and switch /64 block on ban.
    :ivar BALANCING_IP: Balance requests across multiple IP addresses.
    """

    ROTATING_IP = "rotating_ip"
    NANO_IP = "nano_ip"
    ROTATING_NANO_IP = "rotating_nano_ip"
    BALANCING_IP = "balancing_ip"


class IPBlockType(StrEnum):
    """IP block family type.

    :ivar IPV4: IPv4 address block.
    :ivar IPV6: IPv6 address block.
    """

    IPV4 = "inet4"
    IPV6 = "inet6"
