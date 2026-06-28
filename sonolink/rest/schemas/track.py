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

from typing import Any

import msgspec

from ..enums import TrackLoadResult
from .playlist import PlaylistInfo

__all__ = (
    "PlaylistData",
    "Track",
    "TrackDecodeResponse",
    "TrackInfo",
    "TrackLoadingResponse",
    "TracksDecodeResponse",
)


class Track(msgspec.Struct, kw_only=True):
    """Represents a Track payload."""

    encoded: str
    """Base64-encoded track string."""

    info: TrackInfo
    """Track metadata object (:class:`TrackInfo`)."""

    plugin_info: Any = msgspec.field(name="pluginInfo")
    """Additional track info provided by plugins."""

    user_data: Any = msgspec.field(name="userData")
    """Additional track data previously provided (:class:`UpdatePlayerRequest`)."""


class TrackInfo(msgspec.Struct, kw_only=True):
    """Represents metadata for Track, available under :attr:`Track.info`."""

    identifier: str
    """Unique track identifier."""

    uri: str | None = None
    """The track's URI, if available (nullable)."""

    title: str
    """Track title."""

    author: str
    """Track author or artist name."""

    length: int
    """Total length of the track in milliseconds."""

    position: int
    """Current playback position in milliseconds."""

    is_seekable: bool = msgspec.field(name="isSeekable")
    """Whether the track is seekable."""

    is_stream: bool = msgspec.field(name="isStream")
    """Whether the track is a live stream."""

    source_name: str = msgspec.field(name="sourceName")
    """Name of the source manager that provided the track."""

    artwork_url: str | None = msgspec.field(name="artworkUrl", default=None)
    """Artwork URL, if available (nullable)."""

    isrc: str | None = msgspec.field(name="isrc", default=None)
    """International Standard Recording Code (nullable)."""


class TrackLoadingResponse(msgspec.Struct, kw_only=True):
    """Represents a TrackLoadingResponse structure payload."""

    load_type: TrackLoadResult = msgspec.field(name="loadType")
    """Type of load result (:class:`TrackLoadResult`)."""

    data: dict[str, Any] | list[dict[str, Any]] | None
    """Associated load result data, this is a dict that will be converted into a valid object
    in the respective object.
    """


class PlaylistData(msgspec.Struct, kw_only=True):
    """Contains the detailed results of a track load request.

    For playlists, this contains playlist metadata and a list of tracks.
    """

    info: PlaylistInfo
    """Playlist metadata (:class:`PlaylistInfo`)."""

    plugin_info: dict[str, Any] = msgspec.field(name="pluginInfo")
    """Additional data returned by the source plugin."""

    tracks: list[Track]
    """List of loaded tracks (:class:`Track`)."""


TrackDecodeResponse = Track
"""Response type for decoding a single track."""

TracksDecodeResponse = list[Track]
"""Response type for decoding multiple tracks."""
