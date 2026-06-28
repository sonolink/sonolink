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
