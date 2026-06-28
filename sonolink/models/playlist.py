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

from typing import TYPE_CHECKING, Any, Iterator, overload

from ..rest.schemas.track import PlaylistData
from .base import BaseModel
from .track import Playable

if TYPE_CHECKING:
    from ..gateway.client import Client

__all__ = ("Playlist",)


class Playlist(BaseModel[PlaylistData]):
    """Represents a Lavalink Playlist.

    This class wraps the :class:`sonolink.rest.schemas.PlaylistData` schema
    and implements the Sequence protocol to allow iteration over tracks.
    """

    __slots__ = ("_tracks",)

    def __init__(self, *, client: Client[Any], data: PlaylistData) -> None:
        super().__init__(client=client, data=data)
        self._tracks: list[Playable] = [
            Playable(client=client, data=track) for track in data.tracks
        ]

    def __str__(self) -> str:
        return self.name

    def __len__(self) -> int:
        return len(self._tracks)

    @overload
    def __getitem__(self, index: int) -> Playable: ...

    @overload
    def __getitem__(self, index: slice) -> list[Playable]: ...

    def __getitem__(self, index: int | slice) -> Playable | list[Playable]:
        """Returns a track or a slice of tracks from the playlist."""
        return self._tracks[index]

    def __iter__(self) -> Iterator[Playable]:
        """Iterates over the tracks in the playlist."""
        return iter(self._tracks)

    def __contains__(self, item: object) -> bool:
        """Checks if a :class:`sonolink.models.Playable` is in the playlist."""
        return item in self._tracks

    @property
    def name(self) -> str:
        """The name of the playlist."""
        return self._data.info.name

    @property
    def selected(self) -> int:
        """The index of the selected track from Lavalink. Returns -1 if none."""
        return self._data.info.selected_track

    @property
    def tracks(self) -> list[Playable]:
        """A list of :class:`sonolink.models.Playable` objects in this playlist."""
        return self._tracks

    @property
    def playlist_type(self) -> str | None:
        """The type of playlist (e.g., 'album', 'playlist'). Provided by plugins."""
        return self._data.plugin_info.get("type")

    @property
    def url(self) -> str | None:
        """The URL of the playlist, if available."""
        return self._data.plugin_info.get("url")

    @property
    def artwork(self) -> str | None:
        """The artwork URL for the playlist, if available."""
        return self._data.plugin_info.get("artworkUrl")

    @property
    def author(self) -> str | None:
        """The author of the playlist, if available."""
        return self._data.plugin_info.get("author")

    @property
    def extras(self) -> dict[str, Any]:
        """Additional playlist data provided via pluginInfo or custom state."""
        return self._data.plugin_info or {}
