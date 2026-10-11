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
            Playable(client=client, data=track, playlist=self) for track in data.tracks
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
        """Return a track or a slice of tracks from the playlist."""
        return self._tracks[index]

    def __iter__(self) -> Iterator[Playable]:
        """Iterate over the tracks in the playlist."""
        return iter(self._tracks)

    def __contains__(self, item: object) -> bool:
        """Check if a :class:`sonolink.models.Playable` is in the playlist."""
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
