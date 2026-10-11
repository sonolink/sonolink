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

import types
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from ..rest.schemas.track import Track
from .base import BaseModel

if TYPE_CHECKING:
    from ..gateway.client import Client
    from .playlist import Playlist

__all__ = (
    "Album",
    "Artist",
    "Playable",
)


class Album:
    """Represents album metadata usually provided by external plugins like LavaSrc."""

    __slots__ = ("_data",)

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def __repr__(self) -> str:
        return f"<sonolink.Album name={self.name!r}>"

    @property
    def name(self) -> str | None:
        """The name of the album."""
        return self._data.get("albumName")

    @property
    def url(self) -> str | None:
        """The URL to the album."""
        return self._data.get("albumUrl")


class Artist:
    """Represents artist metadata usually provided by external plugins like LavaSrc."""

    __slots__ = ("_data",)

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def __repr__(self) -> str:
        return f"<sonolink.Artist name={self.name!r}>"

    @property
    def name(self) -> str | None:
        """The name of the artist."""
        return self._data.get("artistName")

    @property
    def url(self) -> str | None:
        """The URL to the artist profile."""
        return self._data.get("artistUrl")


class Playable(BaseModel[Track]):
    """Represents a playable track within sonolink.

    This class wraps the raw :class:`sonolink.rest.schemas.Track` schema and provides
    a high-level interface for accessing track metadata and state.
    """

    __slots__ = ("_autoplay", "_extras", "_playlist")

    def __init__(
        self,
        *,
        client: Client[Any],
        data: Track,
        playlist: Playlist | None = None,
    ) -> None:
        super().__init__(client=client, data=data)

        self._autoplay: bool = False
        self._playlist: Playlist | None = playlist
        self._extras: types.SimpleNamespace = types.SimpleNamespace(
            **(data.user_data or {})
        )

    def __str__(self) -> str:
        return self.title

    def __len__(self) -> int:
        """Return the length of the track in milliseconds."""
        return self.length

    def __eq__(self, other: object) -> bool:
        """Check if two tracks are the same based on their encoded string."""
        if isinstance(other, Playable):
            return self.encoded == other.encoded
        return False

    def __hash__(self) -> int:
        """Hashes the track based on its encoded string."""
        return hash(self.encoded)

    @property
    def autoplay(self) -> bool:
        """Whether this track was added by AutoPlay rather than a user.

        .. versionadded:: 1.1.0
        """
        return self._autoplay

    @property
    def identifier(self) -> str:
        """The unique identifier for this track based on its source (e.g., YouTube Video ID)."""
        return self._data.info.identifier

    @property
    def encoded(self) -> str:
        """The base64 encoded string used by Lavalink to identify this track."""
        return self._data.encoded

    @property
    def source_name(self) -> str:
        """The name of the source manager that provided this track (e.g., 'youtube', 'spotify')."""
        return self._data.info.source_name

    @property
    def uri(self) -> str | None:
        """The direct URL to the track, if available."""
        return self._data.info.uri

    @property
    def isrc(self) -> str | None:
        """The International Standard Recording Code for the track, if available."""
        return self._data.info.isrc

    @property
    def title(self) -> str:
        """The title of the track."""
        return self._data.info.title

    @property
    def author(self) -> str:
        """The author or artist of the track."""
        return self._data.info.author

    @property
    def artwork(self) -> str | None:
        """A URL to the track's artwork/thumbnail, if available."""
        return self._data.info.artwork_url

    @property
    def album(self) -> Album:
        """The :class:`Album` metadata for this track. Only populated by certain plugins."""
        return Album(self._data.plugin_info or {})

    @property
    def artist(self) -> Artist:
        """The :class:`Artist` metadata for this track. Only populated by certain plugins."""
        return Artist(self._data.plugin_info or {})

    @property
    def playlist(self) -> Playlist | None:
        """The :class:`Playlist` this track belongs to, if any."""
        return self._playlist

    @property
    def length(self) -> int:
        """The total duration of the track in milliseconds."""
        return self._data.info.length

    @property
    def position(self) -> int:
        """The starting position of the track in milliseconds."""
        return self._data.info.position

    @property
    def is_stream(self) -> bool:
        """Whether the track is a live stream."""
        return self._data.info.is_stream

    @property
    def is_seekable(self) -> bool:
        """Whether the track supports seeking."""
        return self._data.info.is_seekable

    @property
    def extras(self) -> types.SimpleNamespace:
        """Additional custom data attached to this track."""
        return self._extras

    @extras.setter
    def extras(self, value: Mapping[Any, Any] | types.SimpleNamespace) -> None:
        if isinstance(value, Mapping):
            self._extras = types.SimpleNamespace(**value)
        else:
            self._extras = value
